# Contributing

Thank you for your efforts and for being a part of the community. All contributions are
appreciated no matter how small or big. Once you contribute to the code base, your work will
be remembered forever.

## Where to send pull requests

> **NOTE:** Only pull requests to the `community-version` branch will be accepted. Any other
> requests will be declined by default, especially to the `main` branch.

Once your code is tested, your changes will be merged to the `main` branch in the next cycle.

## Code guidelines

### Functions

1. All functions or methods are named lower case and snake case.
2. Must have an explanation of their purpose. Write the explanation surrounded in
   `''' Explanation '''` under the definition `def function() -> None:`. Example:

    ```python
    def function() -> None:
      '''
      This function does nothing, it's just an example for explanation placement!
      '''
    ```

3. The types `(str, list, int, list[str], int | float)` for the parameters and returns must
   be given. Example:

    ```python
    def function(param1: str, param2: list[str], param3: int) -> str:
    ```

4. Putting all that together, some valid examples for function or method declarations would
   be as follows.

    ```python
    def function_name_in_camel_case(parameter1: driver, parameter2: str) -> list[str] | ValueError:
      '''
      This function is an example for code guidelines
      '''
      return [parameter2, parameter2.lower()]
    ```

5. The hashtag comments on top of functions are optional, and are intended for developers
   `# Comments for developers`.

    ```python
    # Enter input text function
    def text_input_by_ID(driver: WebDriver, id: str, value: str, time: float=5.0) -> None | Exception:
        '''
        Enters `value` into the input field with the given `id` if found, else throws NotFoundException.
        - `time` is the max time to wait for the element to be found.
        '''
        username_field = WebDriverWait(driver, time).until(EC.presence_of_element_located((By.ID, id)))
        username_field.send_keys(Keys.CONTROL + "a")
        username_field.send_keys(value)
    ```

### Variables

1. All variables must start with lower case and must be in explainable full words. If
   someone reads the variable name, it should be easy to understand what the variable
   stores.
2. All local variables are camel case. Examples:

    ```python
    jobListingsElement = None
    ```

    ```python
    localBufferTime = 5.5
    ```

3. All global variables are snake case. Example:

    ```
    total_runs = 1
    ```

4. Mentioning types is optional.

    ```python
    localBufferTime: float | int = 5.5
    ```

### Configuration variables

1. All config variables are treated as global variables. They have some extra guidelines.
2. Must have a variable setting explanation, and examples of valid values. Examples:

    ```python
    # Explanation of what this setting will do, and instructions to enter it correctly
    config_variable = "value1"    #  <Valid values examples, and NOTES> "value1", "value2", etc. Don't forget quotes ("")
    ```

    ```python
    # Do you want to randomize the search order for search_terms?
    randomize_search_order = False     # True of False, Note: True or False are case-sensitive
    ```

    ```python
    # Avoid applying to jobs if their required experience is above your current_experience. (Set value as -1 if you want to apply to all ignoring their required experience...)
    current_experience = 5             # Integers > -2 (Ex: -1, 0, 1, 2, 3, 4...)
    ```

    ```python
    # Search location, this will be filled in "City, state, or zip code" search box. If left empty as "", tool will not fill it.
    search_location = "United States"               # Some valid examples: "", "United States", "India", "Chicago, Illinois, United States", "90001, Los Angeles, California, United States", "Bengaluru, Karnataka, India", etc.
    ```

3. Add the config variable to the appropriate `/config/` file.
4. Every config variable must be validated. Go to `/modules/validator.py` and add it there.
   Example: for the config variable `search_location = ""` found in `/config/search.py`,
   string validation is added in `/modules/validator.py` under the method
   `def validate_search()`.

    ```python
    def validate_search() -> None | ValueError | TypeError:
        '''
        Validates all variables in the `/config/search.py` file.
        '''
        check_string(search_location, "search_location")
    ```

5. If the setting should also appear in the local control panel, add it to
   `config_schema.py`. Settings left out of the schema are still fully usable by editing the
   `config/*.py` file, and the [configuration docs](docs/configuration.md) list which ones
   those are.

## Running the tests

Before opening a PR, run the test suite and make sure it passes:

```
./run_tests.sh          # macOS/Linux  (run_tests.command / run_tests.bat also work)
# or:  python -m pytest
```

## Checklist before opening a PR

- [ ] My PR targets the `community-version` branch.
- [ ] I followed the code guidelines above.
- [ ] I ran the tests (`./run_tests.sh` or `python -m pytest`) and they pass.
- [ ] My contribution is my own work, or I have the right to submit it, and is offered under the MIT License.

## Licensing of contributions

This project is licensed under the **MIT License** (see [`LICENSE`](LICENSE)). By opening a
pull request you agree that your contribution is your own work (or that you have the right
to submit it) and that it is provided under the MIT License — inbound contributions are
under the same license as the project (inbound = outbound). Contributors are credited
through the Git history.

Optionally, you may add an attestation comment above your code to credit yourself:

```python
##> ------ <Your full name> : <github id> OR <email> - <Type of change> ------
    # your code
##<
```

It is optional and used only for credit. Past contributors are acknowledged in
[`docs/contributor-consent/contributors.md`](docs/contributor-consent/contributors.md).

Thank you for helping improve the project!
