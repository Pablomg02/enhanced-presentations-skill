# Finds a headless Chrome/Chromium. Can be forced with CHROME=/path/to/binary.
if [ -z "$CHROME" ]; then
  for c in ~/.cache/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell \
           ~/Library/Caches/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-mac*/chrome-headless-shell \
           ~/Library/Caches/ms-playwright/chromium-*/chrome-mac/Chromium.app/Contents/MacOS/Chromium \
           "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
           "/Applications/Chromium.app/Contents/MacOS/Chromium" \
           "$(command -v chrome)" "$(command -v chromium)" "$(command -v chromium-browser)" "$(command -v google-chrome)"; do
    [ -x "$c" ] && CHROME="$c" && break
  done
fi
[ -x "$CHROME" ] || { echo "Chrome/Chromium not found: set CHROME=/path" >&2; exit 1; }
CHROME_FLAGS="--headless --no-sandbox --no-zygote --single-process --disable-gpu --hide-scrollbars"
