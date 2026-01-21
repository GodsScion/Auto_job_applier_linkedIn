#!/usr/bin/env python3
"""
Verification script for Message button selectors in LinkedIn job pages.
Tests selectors against HTML dumps in the results/ directory.
"""

import os
import glob
from lxml import html, etree
from typing import List, Dict, Tuple
import json


def find_html_files(results_dir: str = "results") -> List[str]:
    """Find all HTML files in the results directory and subdirectories."""
    html_files = []
    for root, dirs, files in os.walk(results_dir):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    return html_files


def parse_html_file(file_path: str) -> html.HtmlElement:
    """Parse HTML file and return root element."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return html.fromstring(content)
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return None


def find_hiring_team_section(tree: html.HtmlElement) -> List[html.HtmlElement]:
    """Find 'Meet the hiring team' sections in the HTML."""
    # XPath to find the hiring team header
    hiring_team_xpath = "//h2[contains(@class, 'text-heading-medium') and contains(normalize-space(.), 'Meet the hiring team')]"

    headers = tree.xpath(hiring_team_xpath)
    sections = []

    for header in headers:
        # Find the parent artdeco-card
        section = header.xpath("./parent::div[contains(@class, 'artdeco-card')]")
        if section:
            sections.append(section[0])

    return sections


def test_selector_on_section(section: html.HtmlElement, selector: str, profile_id: str = None) -> List[html.HtmlElement]:
    """Test a single selector on a section, optionally with profile ID."""
    try:
        if profile_id:
            # Replace profile_id placeholder in selector
            selector = selector.replace("profile_id',", f"'{profile_id}'")

        # Convert XPath selector to work with lxml (no double slashes at start for relative)
        if selector.startswith("//"):
            # For absolute XPath, we can use it directly
            elements = section.xpath(selector)
        else:
            # For relative XPath, prepend .//
            if not selector.startswith(".//"):
                selector = ".//" + selector
            elements = section.xpath(selector)

        return elements
    except Exception as e:
        print(f"Error testing selector {selector}: {e}")
        return []


def extract_profile_ids(section: html.HtmlElement) -> List[str]:
    """Extract profile IDs from profile links in the section."""
    profile_ids = []
    try:
        # Find all profile links
        links = section.xpath(".//a[contains(@href, '/in/')]")
        for link in links:
            href = link.get('href', '')
            if '/in/' in href:
                profile_id = href.split('/in/')[-1].split('/')[0].split('?')[0]
                if profile_id and profile_id not in profile_ids:
                    profile_ids.append(profile_id)
    except Exception as e:
        print(f"Error extracting profile IDs: {e}")

    return profile_ids


def verify_selectors_on_file(file_path: str) -> Dict:
    """Test all message button selectors on a single HTML file."""
    print(f"\n🔍 Testing selectors on: {file_path}")

    tree = parse_html_file(file_path)
    if not tree:
        return {"file": file_path, "error": "Failed to parse HTML"}

    # Find hiring team sections
    sections = find_hiring_team_section(tree)
    print(f"   Found {len(sections)} 'Meet the hiring team' sections")

    if not sections:
        return {"file": file_path, "error": "No hiring team sections found"}

    results = {
        "file": file_path,
        "sections": []
    }

    # Message button selectors from recruiter_messenger.py (lines 664-685)
    message_button_selectors = [
        # PRIMARY: Exact path from profile link through hirer-card__hirer-information to entry-point
        "//a[contains(@href, '/in/{profile_id}')]/following-sibling::div[contains(@class, 'hirer-card__hirer-information')]/following-sibling::div[contains(@class, 'entry-point')]/button[contains(text(), 'Message')]",

        # Alternative: Entry-point as direct sibling of profile link (previous selector)
        "//a[contains(@href, '/in/{profile_id}')]/following-sibling::div[contains(@class, 'entry-point')]//button[contains(., 'Message')]",

        # Structural: Within hirer-card container structure
        "//div[contains(@class, 'hirer-card__hirer-information')]//a[contains(@href, '/in/{profile_id}')]/ancestor::div[contains(@class, 'display-flex')]//following-sibling::div[contains(@class, 'entry-point')]//button[contains(text(), 'Message')]",

        # Relative: Button within same ancestor container
        "//a[contains(@href, '/in/{profile_id}')]/ancestor::div[contains(@class, 'hirer-card') or contains(@class, 'display-flex')]//div[contains(@class, 'entry-point')]//button[contains(text(), 'Message')]",

        # Broad search: Any entry-point near the profile link
        "//a[contains(@href, '/in/{profile_id}')]//ancestor::div[contains(@class, 'hirer-card')]/following-sibling::div[contains(@class, 'entry-point')]//button[contains(text(), 'Message')]",

        # Fallback: Artdeco button with Message span text in same container
        "//a[contains(@href, '/in/{profile_id}')]/ancestor::div[contains(@class, 'display-flex') and contains(@class, 'align-items-center')]//button[contains(@class, 'artdeco-button') and .//span[contains(text(), 'Message')]]",

        # Last resort: Any artdeco-button with Message text near the profile, excluding msg-overlay
        "//div[not(contains(@class, 'msg-overlay'))]//a[contains(@href, '/in/{profile_id}')]/ancestor::div[1]//button[contains(@class, 'artdeco-button')]//span[contains(text(), 'Message')]/ancestor::button",
    ]

    for section_idx, section in enumerate(sections):
        print(f"   Testing section {section_idx + 1}...")

        section_result = {
            "section_index": section_idx,
            "profile_ids": extract_profile_ids(section),
            "selector_results": []
        }

        # Test each selector
        for selector_idx, selector_template in enumerate(message_button_selectors):
            selector_name = f"Selector {selector_idx + 1}"

            # Test for each profile ID found in the section
            found_buttons = []
            for profile_id in section_result["profile_ids"]:
                buttons = test_selector_on_section(section, selector_template, profile_id)
                found_buttons.extend(buttons)

            # Also test without profile_id (for selectors that don't use it)
            if "{profile_id}" not in selector_template:
                buttons = test_selector_on_section(section, selector_template)
                found_buttons.extend(buttons)

            # Filter out duplicates and msg-overlay buttons
            valid_buttons = []
            seen_buttons = set()
            for btn in found_buttons:
                btn_classes = btn.get('class', '')
                btn_id = btn.get('id', '')
                btn_text = btn.text_content().strip()

                # Skip msg-overlay buttons
                if 'msg-overlay' in btn_classes or 'msg-overlay' in btn_id:
                    continue

                # Skip non-Message buttons
                if 'Message' not in btn_text:
                    continue

                # Create unique identifier
                btn_key = f"{btn_classes}_{btn_id}_{btn_text}"
                if btn_key not in seen_buttons:
                    seen_buttons.add(btn_key)
                    valid_buttons.append({
                        "text": btn_text,
                        "class": btn_classes,
                        "id": btn_id,
                        "aria_label": btn.get('aria-label', ''),
                        "data_control_name": btn.get('data-control-name', '')
                    })

            selector_result = {
                "selector_index": selector_idx + 1,
                "selector": selector_template,
                "buttons_found": len(valid_buttons),
                "buttons": valid_buttons
            }

            section_result["selector_results"].append(selector_result)
            print(f"     {selector_name}: {len(valid_buttons)} Message buttons found")

        results["sections"].append(section_result)

    return results


def main():
    """Main function to run the verification."""
    print("🚀 Starting Message Button Selector Verification")
    print("=" * 60)

    # Find all HTML files
    html_files = find_html_files()
    print(f"Found {len(html_files)} HTML files to test")

    if not html_files:
        print("❌ No HTML files found in results/ directory")
        print("Please ensure HTML dumps are saved in results/ subdirectories")
        return

    # Test each file
    all_results = []
    for file_path in html_files:
        result = verify_selectors_on_file(file_path)
        all_results.append(result)

    # Generate summary report
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)

    total_sections = 0
    selector_success_count = {i: 0 for i in range(1, 8)}  # 7 selectors

    for result in all_results:
        if "error" in result:
            print(f"❌ {result['file']}: {result['error']}")
            continue

        print(f"✅ {result['file']}:")
        for section in result["sections"]:
            total_sections += 1
            print(f"   Section {section['section_index'] + 1}: {len(section['profile_ids'])} profiles")

            working_selectors = []
            for sel_result in section["selector_results"]:
                if sel_result["buttons_found"] > 0:
                    selector_success_count[sel_result["selector_index"]] += 1
                    working_selectors.append(sel_result["selector_index"])

            if working_selectors:
                print(f"     Working selectors: {working_selectors}")
            else:
                print("     ❌ No selectors found any Message buttons")

    print(f"\n📈 Overall Statistics:")
    print(f"   Total HTML files tested: {len(html_files)}")
    print(f"   Total sections tested: {total_sections}")
    print(f"   Selector success rates:")

    for sel_idx in range(1, 8):
        success_rate = (selector_success_count[sel_idx] / total_sections * 100) if total_sections > 0 else 0
        print(".1f")

    # Save detailed results to JSON
    output_file = "selector_verification_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Detailed results saved to: {output_file}")

    # Identify issues
    print("\n🔍 IDENTIFIED ISSUES:")
    issues = []

    # Check if any selectors never worked
    failed_selectors = [i for i in range(1, 8) if selector_success_count[i] == 0]
    if failed_selectors:
        issues.append(f"Selectors {failed_selectors} never found any Message buttons")

    # Check if primary selector (1) works on all sections
    if selector_success_count[1] < total_sections:
        issues.append(f"Primary selector (1) only worked on {selector_success_count[1]}/{total_sections} sections")

    if not issues:
        print("✅ No major issues identified")
    else:
        for issue in issues:
            print(f"⚠️  {issue}")

    print("\n🎯 RECOMMENDATIONS:")
    print("   1. Use the selector with highest success rate as primary")
    print("   2. Keep multiple selectors as fallbacks")
    print("   3. Test new HTML structures as LinkedIn updates their UI")


if __name__ == "__main__":
    main()