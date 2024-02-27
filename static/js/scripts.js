// mi_script.js

// mi_script.js

document.addEventListener("DOMContentLoaded", function () {
    // URL de la API
    const apiUrl = "https://reborn.assay.cl/api/v1/fs_elec";

    // Realizar la llamada a la API utilizando fetch
    fetch(apiUrl)
        .then((response) => {
            // Verificar si la respuesta es exitosa (código de estado 200)
            if (!response.ok) {
                throw new Error(`Error al llamar a la API: ${response.statusText}`);
            }

            // Convertir la respuesta a formato JSON
            return response.json();
        })
        .then((data) => {
            // Manejar los datos de la respuesta
            mostrarDatosEnTabla(data);
            mostrarTotalElementos(data);
        })
        .catch((error) => {
            // Manejar errores en la llamada a la API
            console.error(error);
        });
});

function mostrarDatosEnTabla(data) {
    // Obtener la tabla en la plantilla por su ID
    const tabla = document.getElementById("miTabla");

    // Iterar sobre los datos y agregar filas a la tabla
    data.data.forEach((item) => {
        const fila = tabla.insertRow(-1);
        const celdaBus = fila.insertCell(0);
        const celdaEstado = fila.insertCell(1);

        celdaBus.textContent = item.vehicle;
        celdaEstado.textContent = obtenerNombreEstado(item.state);
    });
}

function mostrarTotalElementos(data) {
    // Obtener el total de elementos en la respuesta de la API
    const totalElementos = data.data.length;

    // Mostrar el total en el lugar deseado en la plantilla
    const totalElementosContainer = document.getElementById("total-elementos");
    totalElementosContainer.textContent = totalElementos.toString();
}

function obtenerNombreEstado(estado) {
    // Puedes definir una función para obtener un nombre legible para el estado
    switch (estado) {
        case 2:
            return "En Reparacion";
        case 3:
            return "Mantencion";
        default:
            return "Desconocido";
    }
}
