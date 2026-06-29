    tic
    clear all;
    
    % --- Conexión del LCR ---
    visadevObj = "USB0::0x2A8D::0x2F01::MY46620824::0::INSTR";
    instr = visadev(visadevObj); %Establece la comunicación VISA
    comando(instr,'*IDN?') %Verifica conexión
    pause(0.2);
    % --- Configurar lista de frecuencias ---
    freqList = [20, 50, 100, 200, 500, 1e3, 2e3, 5e3, 10e3, 20e3, 50e3, 100e3, 200e3, 500e3, 1e6, 2e6];
    freqString = sprintf('%g,', freqList); 
    freqString(end) = [];
    
    instr.Timeout = 30;  % aumenta tiempo máximo de respuesta
    
    comando(instr, '*RST');                     % Reset del instrumento
    pause(2);
    comando(instr, sprintf('LIST:FREQ %s', freqString)); % Carga lista
    pause(2);  
    
    comando(instr, ':VOLT 1');            % Fija el voltaje del medidor al valor que se desee
    pause(1);
    
    % --- Configurar modo de medida y promedio ---
    comando(instr, ':FUNC:IMP:TYPE ZTD');    % Modo |Z|-Theta (fase en grados)
    pause(2);
    comando(instr, ':CORR:LOAD:TYPE ZTD');    % Modo |Z|-Theta (fase en grados)
    pause(2);
    
    % % Configurar averaging correctamente (sin consultas intermedias)
    comando(instr, ':APER LONG, 16');       % Activa el promedio
    pause(2);
    
    
    
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
