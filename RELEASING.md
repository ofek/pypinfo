# Release Checklist

- [ ] Update the
      [`CHANGELOG.rst`](https://github.com/ofek/pypinfo/blob/master/CHANGELOG.rst)
      and the version in
      [`pypinfo/__init__.py`](https://github.com/ofek/pypinfo/blob/master/pypinfo/__init__.py)

- [ ] Get `master` to the appropriate code release state.
      [GitHub Actions](https://github.com/ofek/pypinfo/actions) should be running
      cleanly for all merges to `master`.
      [![GitHub Actions status](https://github.com/ofek/pypinfo/actions/workflows/test.yml/badge.svg)](https://github.com/ofek/pypinfo/actions/)

- [ ] Create and push a tag, for example:

```bash
git tag -m 23.0.0 23.0.0
git push --tags
```

- [ ] Check the tagged
      [GitHub Actions build](https://github.com/ofek/pypinfo/actions/workflows/deploy.yml)
      has deployed to [PyPI](https://pypi.org/project/pypinfo/#history)

- [ ] Check installation:

```bash
pip3 uninstall -y pypinfo && pip3 install -U pypinfo && pypinfo --version
```
