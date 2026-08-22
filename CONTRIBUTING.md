# Contributing

Thanks for your interest in contributing to **Auto_job_applier_linkedIn**! All
contributions are welcome, no matter how small or large.

## 1. Follow the existing code guidelines

This project already documents its code style, naming conventions, configuration-variable
rules, and the **attestation format** for contributions. Please read and follow the
**Contributor Guidelines** section of the [README](README.md#-contributor-guidelines)
rather than duplicating it here. In particular:

- **Code guidelines** — function naming/docstrings/type hints, variable naming, and
  configuration-variable rules: see [README → Code Guidelines](README.md#code-guidelines).
- **Attestation** — every contribution needs an attestation marker in the code, in the
  form:

  ```python
  ##> ------ <Your full name> : <github id> OR <email> - <Type of change> ------
      # your code
  ##<
  ```

  See [README → Attestation](README.md) for full examples. Keeping accurate attestation
  markers also helps us maintain the contributor records in
  [`docs/contributor-consent/contributors.md`](docs/contributor-consent/contributors.md).

## 2. Where to send pull requests

Per the README, **pull requests should target the `community-version` branch**, not
`main`. PRs to other branches (especially `main`) are declined by default. Once your
change is tested, it is merged into `main` in the next cycle. See
[README → Contributor Guidelines](README.md#-contributor-guidelines) for details.

## 3. Quick checklist before opening a PR

- [ ] My PR targets the `community-version` branch.
- [ ] I followed the code and attestation guidelines in the [README](README.md#-contributor-guidelines).
- [ ] I added an attestation marker for my change.
- [ ] My contribution is my own work, or I have the right to submit it.

## 4. Licensing of contributions

This project is licensed under the **MIT License** (see [`LICENSE`](LICENSE)). By
opening a pull request, you agree that your contribution is your own work (or that
you have the right to submit it) and that it is provided under the MIT License —
that is, inbound contributions are under the same license as the project (inbound =
outbound).

Thank you for helping improve the project!
