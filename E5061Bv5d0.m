% Control del Keysight E5061B – Medida de Impedancia
% Guardado de módulo y fase en CSV

clear; clc;

% Si la calibración se ha realizado, calOK=1. Si no, calOK=0
CalOK=1; 

%% Preguntar código de usuario 
userCode = input('Introduce tu código de usuario (2 dígitos): ', 's');

%% Configuración VISA
% La dirección física del analizador conectado por USB.
visaAddress = 'USB0::0x0957::0x1309::MY49102232::0::INSTR';

% Crea un objeto de comunicación VISA para hablar con el instrumento
% Keysight. En versiones más recientes es mejor utilizar el comando devvisa
v = visa('keysight', visaAddress);

% Amplía la memoria reservada para recibir datos a 10 Megabytes. 
v.InputBufferSize = 10e6;   

% Tiempo de espera para recibir respuesta del Keysight.
v.Timeout = 60;             
fopen(v);

%Comprobación de errores
try
    %% Comprobación del instrumento
    % Este comando pide al equipo que se identifique.
    fprintf(v, '*IDN?');
    
    % Lee la respuesta de texto que el equipo ha enviado al buffer y la guarda en 'idn'.
    idn = fgetl(v);
    
    % Imprime en la consola de MATLAB el texto de identificación que devolvió el equipo.
    fprintf('Instrumento detectado: %s\n', idn);
    
    %% Configuracion Y calibracion
    % Evalúa si la variable CalOK es 0. Si se define como 1 este bloque no se lanza.
    if(CalOK==0)
        %% Configuración del barrido
        % Envía comando para configurar el eje X del barrido en escala Logarítmica.
        fprintf(v, 'SENS1:SWE:TYPE LOG');  
        % Fija la frecuencia de inicio del barrido en 20 Hz.
        fprintf(v, 'SENS1:FREQ:STAR 20');  
        % Fija la frecuencia de finalización del barrido en 2 MHz (2E6 Hz).
        fprintf(v, 'SENS1:FREQ:STOP 2E6');  
        % Establece el número de puntos de medida por barrido en 100.
        fprintf(v, 'SENS1:SWE:POIN 100');  
        % Configura el ancho de banda del filtro de frecuencia intermedia (IFBW) a 10 Hz.
        fprintf(v, 'SENS1:BWID 10');        
        
        % Averaging
        % Borra los datos previos que el instrumento tuviera en su buffer de promediado.
        fprintf(v, 'SENS1:AVER:CLE');       
        % Enciende la función de promediado en el analizador.
        fprintf(v, 'SENS1:AVER ON');        
        % Le indica al analizador que haga una media aritmética de 8 barridos sucesivos.
        fprintf(v, 'SENS1:AVER:COUN 8');    
        
        % Pausa para calibración y selección de modo
        % Muestra una ventana emergente (msgbox) que frena el código ('modal' y 'uiwait') 
        % hasta que el usuario hace clic en "OK".
        uiwait(msgbox(['Especificar modo de medida en el E5061B, ', ...
                       'seleccionar |Z| y realizar la calibración. Conecta tu dispositivo', ...
                       'Pulse OK cuando esté listo.'],...
                       'Calibración y Selección','modal'));
                       
        % Llama a la función personalizada (al final del script) que usa Windows para hablar.
        AudioMessage('Ve al menu Measurement y selecciona Impedance analysis.');
        % Pausa la ejecución de MATLAB 1 segundo para dar tiempo a escuchar el mensaje.
        pause (1)
        AudioMessage('Pulsa en Method y selecciona Port 1 2 Shunt');
        pause (1) 
        AudioMessage('Selecciona módulo de Z, realiza la calibración, y pulsa OK.');
    end 

    % Más mensajes de voz y ventanas emergentes para guiar al usuario
    AudioMessage('Conecta tu dispositivo. Pulsa OK cuando termine el promediado.');
    uiwait(msgbox('Conecta tu dispositivo. Pulse OK cuando termine el barrido y el promediado en el E5061B.',...
                  'Esperando Averaging','modal'));
   
    %% Guardar traza de módulo de Z
    % Crea dinámicamente el nombre del archivo concatenando el código de usuario con 'M.csv'
    modFile = [userCode 'M.csv'];
    
    % Envía el comando SCPI para que el analizador guarde el archivo en su memoria.
    fprintf(v, [':MMEM:STOR:FDAT "' modFile '"']);  
    
    % Muestra una ventana confirmando que se ha guardado el archivo del módulo.
    uiwait(msgbox(['Traza módulo guardado en: ' modFile],'Traza módulo'));
    
    %% Mensaje para seleccionar manualmente la fase
    AudioMessage('Datos de módulo guardados. Ahora selecciona manualmente la fase para la traza activa y pulsa OK.');
    uiwait(msgbox('Ahora selecciona manualmente la fase para la traza activa en el E5061B y pulsa OK.',...
                  'Selección de Fase','modal'));
                  
    %% Guardar traza de fase
    % Crea el nombre del archivo para la fase concatenando el usuario con 'A.csv' (Angle)
    angleFile = [userCode 'A.csv'];
    
    % Envía el comando al instrumento para guardar los nuevos datos en pantalla.
    fprintf(v, [':MMEM:STOR:FDAT "' angleFile '"']);  
    
    % Imprime en la consola de MATLAB un resumen de los archivos creados.
    fprintf('Guardado completado: módulo en %s, fase en %s\n', modFile, angleFile);

% Si ocurrió algún error en todo el bloque 'try' se escribe en la consola el error que ha ocurrido.
catch ME
    warning('Ocurrió un error: %s', ME.message);
end

%% Cerrar VISA
AudioMessage('La medida ha concluido. Cerramos dispositivo');


fclose(v);
delete(v);
clear v;

% Declaración de la función personalizada para emitir mensajes de voz
function AudioMessage(text)
    % Usa el comando 'system' para ejecutar código de Windows PowerShell desde MATLAB.
    % Invoca a 'System.Speech' que es la API de síntesis de voz de Windows y le manda a leer
    % en voz alta la cadena de texto que se pasó como argumento a la función.
    system(['PowerShell -Command "Add-Type -AssemblyName System.Speech; ' ...
            '$speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; ' ...
            '$speak.Speak(''', text, ''');"']);
end