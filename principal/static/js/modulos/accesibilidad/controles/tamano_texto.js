// CAMBIO GUÍA 4: reubicado en la estructura modular de JavaScript.
(() => {
    const storageKey = 'el-paso-text-size';
    const availableSizes = [100, 110, 120, 130, 140, 150, 160];
    let currentSize = 100;

    try {
        const savedSize = Number(window.localStorage.getItem(storageKey));
        if (availableSizes.includes(savedSize)) {
            currentSize = savedSize;
        }
    } catch (error) {
        console.warn('No se pudo leer la preferencia de tama\u00f1o de texto.', error);
    }

    const controls = document.createElement('section');
    controls.className = 'accessibility-controls';
    controls.setAttribute('role', 'region');
    controls.setAttribute('aria-label', 'Opciones de lectura');

    const label = document.createElement('span');
    label.className = 'accessibility-controls__label';
    label.textContent = 'Tama\u00f1o del texto';
    controls.append(label);

    function makeButton(text, labelText, onClick) {
        const button = document.createElement('button');
        button.type = 'button';
        button.textContent = text;
        button.setAttribute('aria-label', labelText);
        button.addEventListener('click', onClick);
        controls.append(button);
    }

    const status = document.createElement('span');
    status.className = 'accessibility-controls__status';
    status.setAttribute('role', 'status');
    status.setAttribute('aria-live', 'polite');

    function applySize(savePreference = true) {
        document.documentElement.style.fontSize = `${currentSize}%`;
        status.textContent = `${currentSize}%`;

        if (savePreference) {
            try {
                window.localStorage.setItem(storageKey, String(currentSize));
            } catch (error) {
                console.warn('No se pudo guardar la preferencia de tama\u00f1o de texto.', error);
            }
        }
    }

    makeButton('A\u2212', 'Disminuir tama\u00f1o del texto', () => {
        const index = availableSizes.indexOf(currentSize);
        if (index > 0) {
            currentSize = availableSizes[index - 1];
            applySize();
        }
    });
    makeButton('A+', 'Aumentar tama\u00f1o del texto', () => {
        const index = availableSizes.indexOf(currentSize);
        if (index < availableSizes.length - 1) {
            currentSize = availableSizes[index + 1];
            applySize();
        }
    });
    makeButton('Restablecer', 'Restablecer tama\u00f1o normal del texto', () => {
        currentSize = 100;
        applySize();
    });
    controls.append(status);
    document.body.append(controls);
    applySize(false);
})();
