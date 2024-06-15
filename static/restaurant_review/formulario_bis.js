document.addEventListener('DOMContentLoaded', function() {
    setupFormHandlers();
});

function setupFormHandlers() {
    var form = document.getElementById('upload-form');
    var inputElement = document.getElementById('file-input');
    var customButton = document.getElementById('custom-button');
    var uploadButton = document.getElementById('upload-btn');
    var loadingMessage = document.getElementById('loading-message');
    

    customButton.addEventListener('click', function() {
        inputElement.click();
    });     

    inputElement.addEventListener('change', function() {
        handleInputChange();
        uploadButton.style.display = 'block'; // Mostrar el botón de carga una vez seleccionados los archivos
    });

    // Remover y volver a agregar el manejador de eventos de cambio para inputElement
    inputElement.removeEventListener('change', handleInputChange);
    inputElement.addEventListener('change', handleInputChange);

    function handleInputChange() {
        var fileList = document.getElementById('file-list');
        fileList.innerHTML = ''; // Limpiar la lista previa
        let countPDFs = 0; // Contador para archivos PDF válidos
        const maxFileSize = 614400; // Tamaño máximo en bytes (600 KB)
        const maxValidFiles = 25; // Máximo número de archivos válidos
        let exceededLimit = false; // Indicador si se superó el límite
        let excedetamanho = false;
    
        Array.from(inputElement.files).forEach(function(file) {
            // Solo procesar hasta 30 archivos PDF válidos
            if (file.name.toLowerCase().endsWith('.pdf')) {
                if (file.size <= maxFileSize) { // Verificar el tamaño del archivo
                    if (countPDFs < maxValidFiles) {
                        var li = document.createElement('li');
                        li.textContent = file.name + ' (tamaño: ' + file.size + ' bytes)';
                        fileList.appendChild(li);
                        countPDFs++; // Incrementar contador si el archivo es PDF y tiene tamaño adecuado
                    } else {
                        // Marcar que se ha superado el límite
                        exceededLimit = true;
                    }
                } else {
                    excedetamanho = true;
                }
            }
        });
        // Mostrar mensajes si algún archivo supero el tamaño de 600K y/o se supera el límite de 30 archivos válidos
        if (excedetamanho) {
            var li = document.createElement('li');
            li.textContent = ' Se descartaron PDFs de tamaño superior a 600K';
            fileList.appendChild(li);
        }
        if (exceededLimit) {
            var li = document.createElement('li');
            li.textContent = ' El máximo número de PDFs válidos es 25, por favor cargue el resto desde otra carpeta';
            fileList.appendChild(li);
        }       
        uploadButton.style.display = countPDFs > 0 ? 'block' : 'none';
    }

    // Remover y volver a agregar el manejador de eventos de clic para uploadButton
    uploadButton.removeEventListener('click', handleUploadClick);
    uploadButton.addEventListener('click', handleUploadClick);


    function handleUploadClick() {
        // Mostrar el mensaje de carga y actualizar dinámicamente
        loadingMessage.style.display = 'block';
        updateLoadingMessage(0);  // Iniciar la actualización del mensaje de carga

        var formData = new FormData(form);
        var csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        formData.append('csrfmiddlewaretoken', csrfToken);
        let countPDFs = 0; // Contador para archivos PDF válidos
        const maxFileSize = 614400; // Tamaño máximo en bytes (600 KB)
        const maxValidFiles = 25; // Máximo número de archivos válidos        
        Array.from(inputElement.files).forEach(function(file) {
            if (file.name.endsWith('.pdf')) {
                if (countPDFs < maxValidFiles) {
                    if (file.size <= maxFileSize) { // Verificar el tamaño del archivo
                        formData.append('files', file, file.name);
                        countPDFs++; 
                        }
                    }
                }
            }
        );


        // Realizar la solicitud de carga con fetch
        fetch(form.action, {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = data.redirect_url;  // Redirigir usando JavaScript
            } else {
                console.log('Algo salió mal durante la carga');
            }
        })
        .catch(error => {
            console.error('Error en la carga:', error);
        });
    }

    function updateLoadingMessage(count) {
        loadingMessage.textContent = 'Cargando archivos' + '.'.repeat(count % 4);
        setTimeout(function() {
            updateLoadingMessage(count + 1);
        }, 1000);
    }
}
