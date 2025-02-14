import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import numpy as np
import random
import math
import time
import threading
from collections import defaultdict

class Node:
    def __init__(self, node_id, is_malicious=False):
        self.node_id = node_id
        self.is_malicious = is_malicious
        self.reputation = 1.0
        self.energy = 100.0
        self.position = (random.uniform(0, 100), random.uniform(0, 100))
        self.neighbors = set()
        self.q_table = defaultdict(lambda: defaultdict(float))

    def update_position(self, new_x, new_y):
        self.position = (new_x, new_y)

class MANET:
    def __init__(self, num_nodes=15, malicious_ratio=0.1):
        self.nodes = {}
        self.transmission_range = 30
        num_malicious = int(num_nodes * malicious_ratio)
        
        for i in range(num_nodes):
            self.nodes[i] = Node(i, is_malicious=(i < num_malicious))
        
        self.update_topology()
    
    def update_topology(self):
        for node in self.nodes.values():
            node.neighbors.clear()
            for other_id, other_node in self.nodes.items():
                if node.node_id != other_id:
                    dx = node.position[0] - other_node.position[0]
                    dy = node.position[1] - other_node.position[1]
                    distance = math.sqrt(dx*dx + dy*dy)
                    if distance <= self.transmission_range:
                        node.neighbors.add(other_id)

class EnhancedMANETVisualizer(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.title("Enhanced MANET Routing Visualization")
        self.geometry("1400x900")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Initialize MANET
        self.manet = MANET(num_nodes=15)
        self.selected_node = None
        self.animation_speed = 1.0
        self.is_simulating = False
        self.packet_routes = []
        self.success_count = 0
        self.total_routes = 0
        
        self.create_gui()
        self.setup_styles()
        
    def create_gui(self):
        # Main container with gradient background
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel (70% width) for visualization
        self.viz_frame = ctk.CTkFrame(self.main_frame)
        self.viz_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Network canvas with dark theme
        self.canvas = tk.Canvas(
            self.viz_frame,
            background='#1a1a1a',
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        
        # Right panel (30% width) for controls
        self.control_panel = ctk.CTkFrame(self.main_frame, width=400)
        self.control_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5, pady=5)
        
        self.create_control_panel()
        
    def create_control_panel(self):
        # Title
        title = ctk.CTkLabel(
            self.control_panel,
            text="MANET Control Center",
            font=("Helvetica", 24, "bold")
        )
        title.pack(pady=20)
        
        # Simulation Controls
        sim_frame = ctk.CTkFrame(self.control_panel)
        sim_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ctk.CTkLabel(sim_frame, text="Simulation Controls", font=("Helvetica", 16, "bold")).pack(pady=10)
        
        # Start/Stop button with gradient effect
        self.start_button = ctk.CTkButton(
            sim_frame,
            text="Start Simulation",
            command=self.toggle_simulation,
            fg_color=("#28a745", "#218838"),
            hover_color=("#218838", "#1e7e34"),
            height=40
        )
        self.start_button.pack(fill=tk.X, padx=20, pady=10)
        
        # Speed control with modern slider
        speed_frame = ctk.CTkFrame(sim_frame)
        speed_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ctk.CTkLabel(speed_frame, text="Animation Speed").pack(side=tk.LEFT, padx=5)
        
        self.speed_slider = ctk.CTkSlider(
            speed_frame,
            from_=0.1,
            to=3.0,
            number_of_steps=29,
            command=self.update_speed
        )
        self.speed_slider.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)
        self.speed_slider.set(1.0)
        
        # Network Statistics
        stats_frame = ctk.CTkFrame(self.control_panel)
        stats_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ctk.CTkLabel(stats_frame, text="Network Statistics", font=("Helvetica", 16, "bold")).pack(pady=10)
        
        self.stats_labels = {}
        stats = [
            ("nodes", "Total Nodes"),
            ("malicious", "Malicious Nodes"),
            ("success_rate", "Success Rate"),
            ("active_routes", "Active Routes"),
            ("avg_energy", "Average Energy")
        ]
        
        for key, text in stats:
            frame = ctk.CTkFrame(stats_frame)
            frame.pack(fill=tk.X, padx=10, pady=5)
            ctk.CTkLabel(frame, text=text).pack(side=tk.LEFT, padx=5)
            self.stats_labels[key] = ctk.CTkLabel(frame, text="0")
            self.stats_labels[key].pack(side=tk.RIGHT, padx=5)
        
        # Node Controls
        node_frame = ctk.CTkFrame(self.control_panel)
        node_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ctk.CTkLabel(node_frame, text="Node Controls", font=("Helvetica", 16, "bold")).pack(pady=10)
        
        btn_frame = ctk.CTkFrame(node_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Add Node",
            command=self.add_node,
            width=120
        ).pack(side=tk.LEFT, padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Remove Node",
            command=self.remove_node,
            width=120
        ).pack(side=tk.RIGHT, padx=5)
        
        # Selected Node Info
        self.node_info_frame = ctk.CTkFrame(self.control_panel)
        self.node_info_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ctk.CTkLabel(
            self.node_info_frame,
            text="Selected Node Information",
            font=("Helvetica", 16, "bold")
        ).pack(pady=10)
        
        self.node_info_labels = {}
        info_fields = ["ID", "Position", "Energy", "Reputation", "Neighbors"]
        
        for field in info_fields:
            frame = ctk.CTkFrame(self.node_info_frame)
            frame.pack(fill=tk.X, padx=10, pady=2)
            ctk.CTkLabel(frame, text=field).pack(side=tk.LEFT, padx=5)
            self.node_info_labels[field] = ctk.CTkLabel(frame, text="-")
            self.node_info_labels[field].pack(side=tk.RIGHT, padx=5)
    
    def setup_styles(self):
        self.colors = {
            'normal_node': '#00ff00',
            'malicious_node': '#ff4444',
            'selected_node': '#ffff00',
            'connection': '#404040',
            'active_route': '#00ffff',
            'text': '#ffffff'
        }
        self.node_radius = 12
        
    def toggle_simulation(self):
        self.is_simulating = not self.is_simulating
        if self.is_simulating:
            self.start_button.configure(
                text="Stop Simulation",
                fg_color=("#dc3545", "#c82333")
            )
            threading.Thread(target=self.simulation_loop, daemon=True).start()
        else:
            self.start_button.configure(
                text="Start Simulation",
                fg_color=("#28a745", "#218838")
            )
    
    def simulation_loop(self):
        while self.is_simulating:
            # Update node positions
            for node in self.manet.nodes.values():
                new_x = node.position[0] + random.uniform(-2, 2)
                new_y = node.position[1] + random.uniform(-2, 2)
                node.update_position(
                    max(0, min(100, new_x)),
                    max(0, min(100, new_y))
                )
                node.energy = max(0, node.energy - 0.1)
            
            self.manet.update_topology()
            
            self.update_visualization()
            self.update_statistics()
            
            time.sleep(self.animation_speed)
    
    def update_visualization(self):
        self.canvas.delete("all")
        
        # Draw connections between nodes
        for node in self.manet.nodes.values():
            x, y = self.scale_coordinates(node.position)
            for neighbor_id in node.neighbors:
                neighbor = self.manet.nodes[neighbor_id]
                neighbor_x, neighbor_y = self.scale_coordinates(neighbor.position)
                self.canvas.create_line(
                    x, y, neighbor_x, neighbor_y,
                    fill=self.colors['connection'],
                    width=2
                )
        
        # Draw nodes
        for node in self.manet.nodes.values():
            x, y = self.scale_coordinates(node.position)
            color = self.colors['malicious_node'] if node.is_malicious else self.colors['normal_node']
            if node.node_id == self.selected_node:
                color = self.colors['selected_node']
            
            # Node Circle
            self.canvas.create_oval(
                x - self.node_radius, y - self.node_radius,
                x + self.node_radius, y + self.node_radius,
                fill=color, outline=self.colors['connection'],
                width=2
            )
            
            # Node ID label
            self.canvas.create_text(
                x, y,
                text=str(node.node_id),
                fill=self.colors['text'],
                font=("Helvetica", 10, "bold")
            )
    
    def scale_coordinates(self, position):
        return position[0] * 10, position[1] * 10
    
    def update_statistics(self):
        # Update statistics
        self.stats_labels['nodes'].configure(text=str(len(self.manet.nodes)))
        self.stats_labels['malicious'].configure(text=str(sum(1 for n in self.manet.nodes.values() if n.is_malicious)))
        self.stats_labels['success_rate'].configure(text=f"{(self.success_count/self.total_routes)*100:.2f}%")
        self.stats_labels['active_routes'].configure(text=str(len(self.packet_routes)))
        self.stats_labels['avg_energy'].configure(text=f"{np.mean([n.energy for n in self.manet.nodes.values()]):.2f}")
    
    def on_canvas_click(self, event):
        # Select a node when clicking on canvas
        for node_id, node in self.manet.nodes.items():
            x, y = self.scale_coordinates(node.position)
            if (event.x - x) ** 2 + (event.y - y) ** 2 <= self.node_radius ** 2:
                self.selected_node = node.node_id
                self.update_node_info()
                break
    
    def update_node_info(self):
        if self.selected_node is None:
            return
        
        node = self.manet.nodes[self.selected_node]
        self.node_info_labels['ID'].configure(text=str(node.node_id))
        self.node_info_labels['Position'].configure(text=f"({node.position[0]:.2f}, {node.position[1]:.2f})")
        self.node_info_labels['Energy'].configure(text=f"{node.energy:.2f}")
        self.node_info_labels['Reputation'].configure(text=f"{node.reputation:.2f}")
        self.node_info_labels['Neighbors'].configure(text=", ".join(map(str, node.neighbors)))
    
    def update_speed(self, value):
        self.animation_speed = float(value)
    
    def add_node(self):
        new_node_id = len(self.manet.nodes)
        self.manet.nodes[new_node_id] = Node(new_node_id)
        self.manet.update_topology()
        self.update_visualization()
        self.update_statistics()

    def remove_node(self):
        if len(self.manet.nodes) > 0:
            node_to_remove = random.choice(list(self.manet.nodes.keys()))
            del self.manet.nodes[node_to_remove]
            self.manet.update_topology()
            self.update_visualization()
            self.update_statistics()

if __name__ == "__main__":
    app = EnhancedMANETVisualizer()
    app.mainloop()
