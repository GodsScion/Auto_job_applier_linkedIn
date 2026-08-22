# Acknowledgements & MIT relicense record

This project moved from **AGPL-3.0** to the **MIT License** in August 2026.

Rather than ask each past external contributor for permission to relicense their
already-merged code, the source tree was reworked so it contains only work authored
by the maintainer:

- The dedicated per-provider AI connectors were **removed** and replaced with a new
  provider-agnostic AI layer built on **LangChain + LangGraph** (`modules/ai/`).
- Every other external contribution was **removed or independently reimplemented**
  from a description of its behaviour.

As a result, the current (MIT) source tree is an independent implementation. Earlier
commits remain under AGPL-3.0 in the Git history. See [`NOTICE`](../../NOTICE).

## Thanks to past contributors

With gratitude to everyone who contributed to the AGPL-era project. The features
listed below were part of that earlier version; the current MIT codebase reimplements
the same functionality from scratch.

| Contributor | GitHub | Area they contributed to (AGPL era) |
|-------------|--------|-------------------------------------|
| Karthik Sarode | [`WINDY-WINDWARD`](https://github.com/WINDY-WINDWARD) | Flask app and the "Applied Jobs history" web UI; fuzzy matching for location questions |
| Dheeraj Deshwal | [`Dheeraj9811`](https://github.com/Dheeraj9811) | Answer-unknown-questions-with-AI / user-information feature; a multi-select bug fix |
| Yang Li | [`MARKYangL`](https://github.com/MARKYangL) | DeepSeek AI integration |
| Tim L | [`tozeon`](https://github.com/tozeon) | Refactor toward multi-LLM compatibility |
| Iliya Brook | [`IliyaBrook`](https://github.com/IliyaBrook) | Fallback "Easy Apply" detection |
| ArshCypherZ | [`ArshCypherZ`](https://github.com/ArshCypherZ) | Google Gemini support; date-parsing fixes |
| Jason Fry | [`tillydray`](https://github.com/tillydray) | Made the LLM temperature parameter optional |
| Eric Zhang | [`EricZhang2`](https://github.com/EricZhang2) | Fixed a select-then-deselect bug in the job filters |
| M4NU5 | [`M4NU5`](https://github.com/M4NU5) | Pagination fix |
| yeswanthmaturi | [`yeswanthmaturi`](https://github.com/yeswanthmaturi) | Larger CSV field-size limit and safe CSV truncation |

Thank you all.
