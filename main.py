from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.core.window import Window
import can

class CANDashboard(BoxLayout):
    def __init__(self, **kwargs):
        super(CANDashboard, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 20
        self.padding = 30
        
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
            size_hint=(1, 0.2)_))
        
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
    
    def start_monitoring(self, instance):
        """Initialize CAN bus and start monitoring"""
        try:
            self.can_bus = can.interface.Bus(
                interface='socketcan',  # Change to your interface
                channel='can0',        # Change to your channel
                receive_own_messages=False)
            
            self.is_monitoring = True
            self.start_btn.disabled = True
            self.stop_btn.disabled = False
            self.status_label.text = 'Status: Monitoring CAN data...'
            
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
        self.status_label.text = 'Status: Monitoring stopped'
    
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
            
            # Update UI
            self.rpm_label.text = f'RPM: {self.rpm}'
            self.speed_label.text = f'Speed: {self.speed:.1f} km/h'
            self.temp_label.text = f'Engine Temp: {self.temp:.1f} °C'
            
        except Exception as e:
            self.status_label.text = f'CAN Error: {str(e)}'
            self.stop_monitoring()

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
