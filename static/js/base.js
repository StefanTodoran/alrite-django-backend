var darkMode;

if (getCookieValue("darkMode") === "true") {
    darkMode = true;
    // console.log("Detected stored darkMode preference.");
} else if (getCookieValue("darkMode") === "false") {
    darkMode = false;
    // console.log("Detected stored lightMode preference.");
} else {
    // If the user has no stored preference, check their system settings.
    darkMode = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
}

updateDarkMode();

updateDarkMode();
document.getElementById("light-mode-button").addEventListener("click", toggleDarkMode);
document.getElementById("dark-mode-button").addEventListener("click", toggleDarkMode);

setTimeout(() => {
    // This way every page change doesn't have the page flash white
    // before becoming dark, if the user has dark mode enabled.
    document.body.classList.add("do-transition");
}, 1);

function toggleDarkMode() {
    darkMode = !darkMode;
    setCookieValue("darkMode", darkMode);
    updateDarkMode();
}

// This function updates the body's class. This affects page background, and since 
// the body class also sets css variables contianing colors which all other components
// use, it updates the entire page's styles. This function also swaps the buttons.
function updateDarkMode() {
    if (darkMode) {
        document.body.classList.add("darkMode");
        document.getElementById("light-mode-button").classList.add("hidden");
        document.getElementById("dark-mode-button").classList.remove("hidden");
    } else {
        document.body.classList.remove("darkMode");
        document.getElementById("dark-mode-button").classList.add("hidden");
        document.getElementById("light-mode-button").classList.remove("hidden");
    }
}

function getCookieValue(key) {
    const value = document.cookie
        .split("; ")
        .find((row) => row.startsWith(key + "="))
        ?.split("=")[1];
    return value;
}

function setCookieValue(key, value, age) {
    age = age || 31536000;
    const cookie = `${key}=${value}; max-age=${age}; SameSite=None; path=/`;
    document.cookie = cookie;
  }

for (const elem of document.querySelectorAll('details')) {
    if (elem.id != "") {
        toHide = Array.from(elem.querySelectorAll('.' + elem.id + '-ifopen'))

        if (toHide.length != 0) {
            elem.addEventListener("toggle", () => {
                if (elem.open) {
                    for (const child in toHide) {
                        child.classList.remove('hidden')
                    }
                } else {
                    for (const child in toHide) {
                        child.classList.add('hidden')
                    }
                }
            })
        }
    }
}