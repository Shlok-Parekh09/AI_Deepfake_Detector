## 2025-02-14 - Fix Command Injection in sync_kaggle.py
**Vulnerability:** A command injection vulnerability in `backend/scripts/sync_kaggle.py` was found where a user-provided `--kernel` argument was directly interpolated into an `os.system` call (`command = f"kaggle kernels output {kernel_slug} -p {checkpoints_dir}"`).
**Learning:** Even internal helper scripts intended for Kaggle synchronization can become attack vectors if they process unsanitized user inputs, especially when executing shell commands.
**Prevention:** Avoid `os.system()` entirely. Always use `subprocess.run()` with a list of arguments and `shell=False` (the default) to securely pass arguments to external commands without shell evaluation.
