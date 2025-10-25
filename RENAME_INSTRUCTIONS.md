# Repository Rename Instructions

## Status

✅ **Git remote updated** - Now points to `git@github.com:SullivanXiong/supyx.git`
✅ **Package renamed** - Internal package structure is now `supyx/`
✅ **All code updated** - References to quasarpy changed to supyx
⚠️ **Local directory** - Still named `quasarpy` (locked by process)

## Manual Steps Required

### 1. Rename Local Directory

Close all applications that might have the directory open (Cursor, terminals, file explorers), then:

**Windows PowerShell:**

```powershell
cd C:\Users\SXion\suxiong\repos
Rename-Item -Path "quasarpy" -NewName "supyx"
```

**Or in File Explorer:**

1. Navigate to `C:\Users\SXion\suxiong\repos`
2. Right-click on `quasarpy` folder
3. Select "Rename"
4. Change name to `supyx`

### 2. Rename GitHub Repository

1. Go to https://github.com/SullivanXiong/quasarpy
2. Click "Settings"
3. Scroll to "Repository name"
4. Change from `quasarpy` to `supyx`
5. Click "Rename"

GitHub will automatically redirect from the old URL to the new one.

### 3. Update minimalist Project Path

After renaming the local directory, verify the path in:

`minimalist/client/pyproject.toml`:

```toml
[tool.uv.sources]
supyx = { path = "../../supyx", editable = true }
```

If still using the old directory name temporarily, keep:

```toml
supyx = { path = "../../quasarpy", editable = true }
```

### 4. Verify Everything Works

```bash
cd supyx  # or quasarpy if not renamed yet
python -c "import supyx; print(supyx.__version__)"
# Should print: 0.1.0
```

## What's Already Done

✅ Package code renamed to `supyx/`
✅ `pyproject.toml` updated with name and PyPI metadata  
✅ `README.md` updated with new package name
✅ `supyx/__init__.py` updated
✅ All minimalist docs updated (README, SETUP, PROJECT_SUMMARY, etc.)
✅ `client/app.py` imports from `supyx`
✅ Git remote points to `supyx.git`

## Next: Build & Publish

Once the directory rename is complete (or leaving it as-is is fine for now), proceed with:

```bash
cd quasarpy  # or supyx if renamed
uv build
twine upload dist/*
```

The package name that matters for PyPI is in `pyproject.toml` (already set to "supyx"), not the directory name.
