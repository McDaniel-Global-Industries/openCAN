from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.config import Config
import can
import subprocess
import os

# Configure Kivy for better touch response
Config.set('input', 'mtdev_%(name)s', 'probesysfs')
Config.set('input', 'hid_%(name)s', 'probesysfs')

class CANDashboard(BoxLayout):
    def __init__(self, **kwargs):
        super(CANDashboard, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 20
        self.padding = 30
        
        # CAN configuration
        self.can_interface = 'socketcan'  # Default
        self.can_channel = 'can0'
        self.virtual_mode = False
        
        # CAN bus connection
        self.can_bus = None
        self.is_monitoring = False
        
        # Data variables
        self.rpm = 0
        self.speed = 0
        self.temp = 0
        
        # Create UI elements
        self.title_label = Label(
            text='openCAN Dashboard',
            font_size='24sp',
            bold=True,
            size_hint=(1, 0.2))
        
        # Virtual mode toggle
        self.mode_toggle = ToggleButton(
            text='Virtual Mode: OFF',
            size_hint=(1, 0.1),
            on_press=self.toggle_virtual_mode)
        
        self.rpm_label = Label(
            text='RPM: 0',
            font_size='20sp',
            size_hint=(1, 0.2))
        
        self.speed_label = Label(
            text='Speed: 0 km/h',
            font_size='20sp',
            size_hint=(1, 0.2))
        
        self.temp_label = Label(
            text='Engine Temp: 0 °C',
            font_size='20sp',
            size_hint=(1, 0.2))
        
        # Button layout
        button_layout = BoxLayout(
            orientation='horizontal',
            spacing=20,
            size_hint=(1, 0.2))
        
        self.start_btn = Button(
            text='Start Monitoring',
            on_press=self.start_monitoring)
        
        self.stop_btn = Button(
            text='Stop Monitoring',
            on_press=self.stop_monitoring,
            disabled=True)
        
        button_layout.add_widget(self.start_btn)
        button_layout.add_widget(self.stop_btn)
        
        # Add all widgets to main layout
        self.add_widget(self.title_label)
        self.add_widget(self.mode_toggle)
        self.add_widget(self.rpm_label)
        self.add_widget(self.speed_label)
        self.add_widget(self.temp_label)
        self.add_widget(button_layout)
        
        # Status label
        self.status_label = Label(
            text='Status: Ready',
            font_size='16sp',
            color=(0.8, 0.8, 0.8, 1),
            size_hint=(1, 0.1))
        self.add_widget(self.status_label)
    
    def toggle_virtual_mode(self, instance):
        """Switch between real and virtual CAN mode"""
        self.virtual_mode = not self.virtual_mode
        if self.virtual_mode:
            self.can_interface = 'virtual'
            self.can_channel = 'vcan0'
            instance.text = 'Virtual Mode: ON'
            self.status_label.text = 'Virtual CAN mode enabled'
            self.setup_virtual_can()
        else:
            self.can_interface = 'socketcan'
            self.can_channel = 'can0'
            instance.text = 'Virtual Mode: OFF'
            self.status_label.text = 'Real CAN mode enabled'
    
    def setup_virtual_can(self):
        """Initialize virtual CAN interface"""
        try:
            subprocess.run(['sudo modprobe vcan'], shell=True, check=True)
            subprocess.run(['sudo ip link add dev vcan0 type vcan'], shell=True, check=True)
            subprocess.run(['sudo ip link set up vcan0'], shell=True, check=True)
        except subprocess.CalledProcessError as e:
            self.show_error_popup(f"Failed to setup virtual CAN: {str(e)}")
    
    def start_monitoring(self, instance):
        """Initialize CAN bus and start monitoring"""
        try:
            if self.virtual_mode and not os.path.exists('/sys/class/net/vcan0'):
                self.setup_virtual_can()
            
            self.can_bus = can.interface.Bus(
                interface=self.can_interface,
                channel=self.can_channel,
                receive_own_messages=False)
            
            self.is_monitoring = True
            self.start_btn.disabled = True
            self.stop_btn.disabled = False
            self.status_label.text = f'Monitoring {self.can_channel}...'
            
            # Schedule the update function to run every 100ms
            Clock.schedule_interval(self.update_data, 0.1)
            
        except Exception as e:
            self.status_label.text = f'Error: {str(e)}'
            self.stop_monitoring()
    
    def stop_monitoring(self, instance=None):
        """Stop CAN bus monitoring"""
        self.is_monitoring = False
        Clock.unschedule(self.update_data)
        
        if self.can_bus is not None:
            self.can_bus.shutdown()
            self.can_bus = None
        
        self.start_btn.disabled = False
        self.stop_btn.disabled = True
        self.status_label.text = 'Monitoring stopped'
    
    def update_data(self, dt):
        """Read CAN data and update display"""
        if not self.is_monitoring or self.can_bus is None:
            return
        
        try:
            # Read all available messages
            while True:
                msg = self.can_bus.recv(timeout=0)  # Non-blocking read
                if msg is None:
                    break
                
                # Process CAN message (adjust IDs and parsing for your protocol)
                if msg.arbitration_id == 0x0C1:  # Example RPM message ID
                    self.rpm = int.from_bytes(msg.data[0:2], byteorder='big')
                elif msg.arbitration_id == 0x0C2:  # Example Speed message ID
                    self.speed = int.from_bytes(msg.data[0:2], byteorder='big') / 10
                elif msg.arbitration_id == 0x0C3:  # Example Temp message ID
                    self.temp = msg.data[0]
                
                # In virtual mode, generate simulated data
                if self.virtual_mode:
                    self.generate_virtual_data()
            
            # Update UI
            self.rpm_label.text = f'RPM: {self.rpm}'
            self.speed_label.text = f'Speed: {self.speed:.1f} km/h'
            self.temp_label.text = f'Engine Temp: {self.temp:.1f} °C'
            
        except Exception as e:
            self.status_label.text = f'CAN Error: {str(e)}'
            self.stop_monitoring()
    
    def generate_virtual_data(self):
        """Generate simulated CAN data in virtual mode"""
        self.rpm = (self.rpm + 10) % 8000
        self.speed = (self.speed + 0.5) % 220
        self.temp = 80 + (self.rpm / 200) % 40
    
    def show_error_popup(self, message):
        """Display error messages in a popup"""
        content = Label(text=message)
        popup = Popup(title='Error',
                     content=content,
                     size_hint=(0.8, 0.4))
        content.bind(on_touch_down=popup.dismiss)
        popup.open()

class openCANApp(App):
    def build(self):
        Window.clearcolor = (0.1, 0.1, 0.1, 1)  # Dark background
        return CANDashboard()
    
    def on_stop(self):
        # Clean up when app closes
        if self.root.is_monitoring:
            self.root.stop_monitoring()

if __name__ == '__main__':
    openCANApp().run()
