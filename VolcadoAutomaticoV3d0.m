tic
clear all; 

% Conexión del LCR
visadevObj = "USB0::0x2A8D::0x2F01::MY46620824::0::INSTR";
instr = visadev(visadevObj); %Establece la comunicación VISA a partir del nombre
comando(instr,'*IDN?') %Comprueba la información del LCR Keysight conectado
instr.Timeout = 120;
% ---- Input usuario ----
disp('----- Generador de documento de salida -----');
%Generador de nombre de documento
AudioMessage('Comenzando medida. Por favor, ve a la ventana de comando y teclea tu número identificador')
nomdoc = solicitarNombre('Id: ');
%------------------------


% Realiza la medición con el LCR previamente configurado de forma manual
[Zimp, Phs, freqs, Vac, Iac] = trigger_LCRTemp(instr);

clear('instr')
toc

% Unificar los datos a exportar (ahora con 5 columnas)
data_export = [freqs, Zimp, Phs, Vac, Iac];

% Guarda los datos en el documento Excel
writematrix(data_export, nomdoc);

function nomout = solicitarNombre(msj)
    nomin = input(msj,'s');
    if isempty(nomin)
        nomin = "Id";
    end
    time = clock; hour = num2str(time(4)); min = num2str(time(5));
    nomout = strcat(nomin,hour,'_',min,'.xlsx');
end


% Trigger del sistema para las frecuencias y tipo de medida especificada

% Trigger del sistema para las frecuencias y extracción punto a punto
function [Zimp, Phs, freqs_out, Vac, Iac] = trigger_LCRTemp(instr)  

    % Definimos las frecuencias directamente aquí para el bucle
    freqs = [20, 50, 100, 200, 500, 1e3, 2e3, 5e3, 10e3, 20e3, 50e3, 100e3, 200e3, 500e3, 1e6, 2e6];
    
    % Inicializamos vectores para mayor velocidad
    num_pts = length(freqs);
    Zimp = zeros(num_pts, 1);
    Phs  = zeros(num_pts, 1);
    Vac  = zeros(num_pts, 1);
    Iac  = zeros(num_pts, 1);
    freqs_out = freqs(:); % Asegurar que sea una columna

    comando(instr,'TRIG:SOUR BUS');     % Selecciona el modo de trigger
    comando(instr,'DISP:PAGE MEAS');    % Sale del modo LIST para medición manual
       
    AudioMessage('Realizando medidas punto a punto. Por favor, espera.');
    
    % Bucle de barrido por software
    for i = 1:num_pts
        % 1. Configurar la frecuencia actual
        comando(instr, sprintf(':FREQ %g', freqs(i)));
        
        % 2. Disparar medición
        comando(instr, ':TRIG:IMM');
        
        % 3. Leer Impedancia (Z) y Fase (Theta) principal
        res = comando(instr, ':FETC?');
        res_split = split(res, ",");
        Zimp(i) = str2double(res_split(1));
        Phs(i)  = str2double(res_split(2));
        
        % 4. Leer Monitores de Voltaje (VAC) y Corriente (IAC)
        Vac(i) = str2double(comando(instr, ':FETC:SMON:VAC?'));
        Iac(i) = str2double(comando(instr, ':FETC:SMON:IAC?'));
    end

    % Aviso sonoro y confirmación (ya no hace falta el msgbox manual)
    beepTone(500,0.5); pause(0.5); beepTone(1000,0.25);
    AudioMessage('Medida concluida');
end


% Ejecuta el comando introducido

function ret = comando(g,cmd,varargin)

    % g = Conexión VISA
    % cmd = Comando a ejecutar
    % varargin = Argumento específico de un comando

    % Comprueba que se haya realizado correctamente la conexión
    if isempty(g)
        ME = MException('SpectralM:InterfaceNotsent', 'No interface specified.');
        throw(ME);
    end
    
    %Si se introduce un tercer argumento, se concatena con el comando
    if isempty(varargin) 
         cmdc = char(cmd);
    else
         cmdc = char(sprintf(cmd,varargin{1:end}));
    end
  
    %Ejecución
    flush(g); %Limpia el buffer de entrada y salida antes de la ejecución del comando
    writeline(g,cmdc);

    if cmdc(end) == '?', ret = readline(g); %Si es un comando de consulta, lee la respuesta
    else, ret = '';
    end
    
end

function beepTone(frequency, duration)
    fs = 8192;
    t = 0:1/fs:duration;
    y = sin(2*pi*frequency*t);
    sound(y, fs)
end

function AudioMessage(text)
system(['PowerShell -Command "Add-Type -AssemblyName System.Speech; ' ...
        '$speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; ' ...
        '$speak.Speak(''', text, ''');"']);

end