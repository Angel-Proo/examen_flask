const socket = io();

const area = document.getElementById('area_select');
const puesto = document.getElementById('puesto_select');

area.addEventListener('change', function(){
    let area_id = this.value;
    if (area_id == ''){
        socket.emit('solicitar_puestos', 0)
    }else{
        socket.emit('solicitar_puestos', area_id)
    }
    
    console.log('aqui se emite el socket', area_id)
});

socket.on('puestos',(puestos) =>{
    console.log('llegue',typeof(puestos));

    while (puesto.firstChild){
        puesto.removeChild(puesto.firstChild);
    }

    puestos.forEach((opciones) => {
        const opcion = document.createElement("option");
        opcion.value = opciones.id;
        opcion.text = opciones.puesto;
        puesto.appendChild(opcion);
    });
});

