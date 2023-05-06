
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

