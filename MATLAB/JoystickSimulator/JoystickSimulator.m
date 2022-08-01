function varargout = JoystickSimulator(varargin)
% JOYSTICKSIMULATOR MATLAB code for JoystickSimulator.fig
%      JOYSTICKSIMULATOR, by itself, creates a new JOYSTICKSIMULATOR or raises the existing
%      singleton*.
%
%      H = JOYSTICKSIMULATOR returns the handle to a new JOYSTICKSIMULATOR or the handle to
%      the existing singleton*.
%
%      JOYSTICKSIMULATOR('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in JOYSTICKSIMULATOR.M with the given input arguments.
%
%      JOYSTICKSIMULATOR('Property','Value',...) creates a new JOYSTICKSIMULATOR or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before JoystickSimulator_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to JoystickSimulator_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help JoystickSimulator

% Last Modified by GUIDE v2.5 21-Mar-2022 21:45:32

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @JoystickSimulator_OpeningFcn, ...
                   'gui_OutputFcn',  @JoystickSimulator_OutputFcn, ...
                   'gui_LayoutFcn',  [] , ...
                   'gui_Callback',   []);
if nargin && ischar(varargin{1})
    gui_State.gui_Callback = str2func(varargin{1});
end

if nargout
    [varargout{1:nargout}] = gui_mainfcn(gui_State, varargin{:});
else
    gui_mainfcn(gui_State, varargin{:});
end
end
% End initialization code - DO NOT EDIT


% --- Executes just before JoystickSimulator is made visible.
function JoystickSimulator_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to JoystickSimulator (see VARARGIN)

% Choose default command line output for JoystickSimulator
handles.output = hObject;

% Update handles structure
guidata(hObject, handles);
global leg;
global movement_type;

leg = "R2";
movement_type = 1;

% UIWAIT makes JoystickSimulator wait for user response (see UIRESUME)
% uiwait(handles.figure1);
end

% --- Outputs from this function are returned to the command line.
function varargout = JoystickSimulator_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;
end

% --- Executes during object creation, after setting all properties.
function slider_x_CreateFcn(hObject, eventdata, handles)
% hObject    handle to slider_x (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: slider controls usually have a light gray background.
if isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor',[.9 .9 .9]);
end
end

% --- Executes during object creation, after setting all properties.
function slider_y_CreateFcn(hObject, eventdata, handles)
% hObject    handle to slider_y (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: slider controls usually have a light gray background.
if isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor',[.9 .9 .9]);
end
end

% --- Executes on slider movement.
function slider_y_Callback(hObject, eventdata, handles)
% hObject    handle to slider_y (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'Value') returns position of slider
%        get(hObject,'Min') and get(hObject,'Max') to determine range of slider
global slider_x;
global slider_y;
global angle;

slider_x = get(handles.slider_x,'Value');
slider_y = get(handles.slider_y,'Value');

set(handles.text_x, 'String', num2str(slider_x));
set(handles.text_y, 'String', num2str(slider_y));

% First quadrant
angle = atan(slider_y/slider_x);

% Second quadrant and third quadrant
if slider_x < 0
    angle = pi + angle;
% Fourth quadrant
elseif slider_x >= 0 && slider_y < 0
    angle =  2*pi + angle;
end
end

% --- Executes on slider movement.
function slider_x_Callback(hObject, eventdata, handles)
% hObject    handle to slider_x (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'Value') returns position of slider
%        get(hObject,'Min') and get(hObject,'Max') to determine range of slider
global slider_x;
global slider_y;
global angle;

slider_x = get(handles.slider_x,'Value');
slider_y = get(handles.slider_y,'Value');

set(handles.text_x, 'String', num2str(slider_x));
set(handles.text_y, 'String', num2str(slider_y));

% First quadrant
angle = atan(slider_y/slider_x);

% Second quadrant and third quadrant
if slider_x < 0
    angle = pi + angle;
% Fourth quadrant
elseif slider_x >= 0 && slider_y < 0
    angle =  2*pi + angle;
end

end

% --- Executes on button press in togglebutton_start.
function togglebutton_start_Callback(hObject, eventdata, handles)
% hObject    handle to togglebutton_start (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of togglebutton_start
global start;

start = get(handles.togglebutton_start, 'Value');
end

% --- Executes on button press in checkbox_draw.
function checkbox_draw_Callback(hObject, eventdata, handles)
% hObject    handle to checkbox_draw (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of checkbox_draw
global movement_type;
global slider_x;
global slider_y;
global angle;
global start;
global ee_path;
global leg;

slider_x = get(handles.slider_x,'Value');
slider_y = get(handles.slider_y,'Value');
angle = atan(slider_y/slider_x);

ee_path = [];

i = 1;
a = [];
while get(handles.checkbox_draw, 'Value')
   while start
   
       % If Y and X is at 0, no movement
       if isnan(angle)
           pause(0.01);
           continue;
       end
       
       if movement_type
           coords = ODMovement(60, 50, 50, 50, angle, leg, i); 
          
           i = i + 1;
       else
          coords = RotateMovement(60, 50, 50, 50, leg, i);
          
          if slider_x < 0.0
             i = i - 1;
          else
              i = i + 1;
          end
       end
       
       angles = InverseKinematics(coords);
       DrawLegTrajectory(angles, coords, "Omni Direction", leg);
       a = [a; rad2deg(angles)];
       fprintf("%.3f %.3f %.3f\n", (angles(:, 1) + 90), (angles(:, 2) + 90 - 20.5), (angles(:, 3) + 90 - 100.15))
       
       if size(ee_path, 1) == 60
          save('ee_path');
          set(handles.togglebutton_rotation, 'Value', 0);
          break 
       end
       
       
       
       if i == 61
          i = 1;
       elseif i == 0
           i = 60;
       end
   end
   
   pause(0.01);
   
   if get(handles.checkbox_draw,'Value') == 0
      break; 
   end
end
end

% --- Executes when user attempts to close figure1.
function figure1_CloseRequestFcn(hObject, eventdata, handles)
% hObject    handle to figure1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: delete(hObject) closes the figure
global start;

start = 0;

pause(0.5);

delete(hObject);
end

% --- Executes on button press in togglebutton_clear.
function togglebutton_clear_Callback(hObject, eventdata, handles)
% hObject    handle to togglebutton_clear (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of togglebutton_clear
global ee_path;

ee_path = [];
end

% --- Executes on selection change in listbox1.
function listbox1_Callback(hObject, eventdata, handles)
% hObject    handle to listbox1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns listbox1 contents as cell array
%        contents{get(hObject,'Value')} returns selected item from listbox1
global leg;
global ee_path;

contents = cellstr(get(handles.listbox1,'String'));
leg = contents{get(hObject,'Value')} + "";
ee_path = [];
end

% --- Executes during object creation, after setting all properties.
function listbox1_CreateFcn(hObject, eventdata, handles)
% hObject    handle to listbox1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: listbox controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end
end


% --- Executes on slider movement.
function slider_view_Callback(hObject, eventdata, handles)
% hObject    handle to slider_view (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'Value') returns position of slider
%        get(hObject,'Min') and get(hObject,'Max') to determine range of slider
global slider_view;

slider_view = get(handles.slider_view,'Value');
end

% --- Executes during object creation, after setting all properties.
function slider_view_CreateFcn(hObject, eventdata, handles)
% hObject    handle to slider_view (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: slider controls usually have a light gray background.
if isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor',[.9 .9 .9]);
end

global slider_view;

slider_view = 322.5;
end


% --- Executes on button press in movement_type.
function togglebutton_locomotion_Callback(hObject, eventdata, handles)
% hObject    handle to movement_type (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of movement_type
global movement_type;

movement_type = get(handles.togglebutton_locomotion,'Value');

if movement_type
    set(handles.togglebutton_rotation, 'Value', 0);
else
    set(handles.togglebutton_rotation, 'Value', 1);
end

end

% --- Executes on button press in togglebutton_rotation.
function togglebutton_rotation_Callback(hObject, eventdata, handles)
% hObject    handle to togglebutton_rotation (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of togglebutton_rotation
global movement_type;

if get(handles.togglebutton_rotation,'Value')
    set(handles.togglebutton_locomotion, 'Value', 0);
    movement_type = 0;
else
    set(handles.togglebutton_locomotion, 'Value', 1);
    movement_type = 1;
end

end
