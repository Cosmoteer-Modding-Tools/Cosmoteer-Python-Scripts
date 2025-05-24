# Language Strings Organizer for Cosmoteer Mods

**Language Strings Organizer** is a desktop application designed to help Cosmoteer modders keep translation strings in sync across multiple language files. By using a single base template, it automatically regenerates or updates additional language `.rules` files to match the structure of your base file, pulling in any missing entries and preserving existing translations.

---

## 📋 Features

* **Template‑driven**: Choose one `.rules` file as your base; all other language files follow its structure.
* **Auto‑detection**: Scans your strings directory for `.rules` files and lists each language code.
* **Preview changes**: Inspect regenerated files in an editor tab before applying.
* **Backup safety**: Renames existing files to `*.rules.backup` before saving updates.
* **Dark mode support**: Integrated with `qdarkstyle` if installed.

### Why use this?

Modders often add new strings or parts to a single, English‑based (or Native) file and then translate into other languages. Over time, it’s easy to forget updating other language files, leaving untranslated or mis‑aligned entries. This tool ensures:

1. **Consistency**: All languages mirror the exact key order and sections of your base file.
2. **Completeness**: Missing keys in translations are automatically inserted (with placeholder values).
3. **Maintainability**: Simplifies bulk updates—no more manual copy/paste mistakes.

---

## 🚀 Installation

1. **Clone this repository**

   ```bash
   git clone https://github.com/YourRepo/Cosmoteer-Lang-Organizer.git
   cd Cosmoteer-Lang-Organizer
   ```

2. **Install dependencies**

   * **Windows**:

     ```bat
     setup.bat
     ```
   * **Unix / Mac**:

     ```bash
     ./setup.sh
     ```

3. **Launch the app**

   * **Windows**: `run.bat`
   * **Unix / Mac**: `./run.sh`

> **Note**: Ensure Python 3.8+ is installed and on your `PATH`.

---

## ⚙️ Usage

1. **Select Strings Directory**: Browse to the folder containing your language `.rules` files.
2. **Choose Base File**: Pick one `.rules` file as the template (e.g., `en.rules`).
3. **Select Languages**: Check or uncheck which language files to regenerate. (make sure to uncheck the base file or any other files you don't want to update)
4. **Preview**: Click **Preview** to see changes in tabs.
5. **Apply**: Click **Apply** to overwrite checked files. Backups are created automatically.

![Screenshot of the tool UI](docs/screenshot.png)

---

## 🛠️ Command‑Line Options (Advanced)

*(coming soon)*

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/my‑update`
3. Commit your changes: \`git commit -m "Add feature X"
4. Push to your branch: `git push origin feature/my‑update`
5. Open a Pull Request

Please keep code style aligned with [PEP 8](https://peps.python.org/pep-0008/) and use `black` or `flake8` for linting.

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
