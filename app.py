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
            
            # Simulate packet routing
            source = random.choice(list(self.manet.nodes.keys()))
            dest = random.choice(list(self.manet.nodes.keys()))
            while dest == source:
                dest = random.choice(list(self.manet.nodes.keys()))
            
            path = self.find_path(source, dest)
            if path:
                self.success_count += 1
                self.packet_routes.append(path)
                if len(self.packet_routes) > 5:
                    self.packet_routes.pop(0)
            
            self.total_routes += 1
            
            # Update UI
            self.update_visualization()
            self.update_statistics()
            
            time.sleep(1.0 / self.animation_speed)
    
    def find_path(self, source, dest):
        visited = set()
        path = [source]
        
        def dfs(current):
            if current == dest:
                return True
            
            visited.add(current)
            neighbors = self.manet.nodes[current].neighbors
            
            for next_node in neighbors:
                if next_node not in visited and not self.manet.nodes[next_node].is_malicious:
                    path.append(next_node)
                    if dfs(next_node):
                        return True
                    path.pop()
            
            return False
        
        return path if dfs(source) else None
    
    def update_visualization(self):
        self.canvas.delete("all")
        
        # Draw connections
        for node_id, node in self.manet.nodes.items():
            x1, y1 = self.scale_coordinates(node.position)
            for neighbor in node.neighbors:
                x2, y2 = self.scale_coordinates(self.manet.nodes[neighbor].position)
                self.canvas.create_line(
                    x1, y1, x2, y2,
                    fill=self.colors['connection'],
                    width=1,
                    dash=(4, 4)
                )
        
        # Draw active routes
        for path in self.packet_routes:
            for i in range(len(path)-1):
                node1 = self.manet.nodes[path[i]]
                node2 = self.manet.nodes[path[i+1]]
                x1, y1 = self.scale_coordinates(node1.position)
                x2, y2 = self.scale_coordinates(node2.position)
                self.canvas.create_line(
                    x1, y1, x2, y2,
                    fill=self.colors['active_route'],
                    width=2
                )
        
        # Draw nodes
        for node_id, node in self.manet.nodes.items():
            x, y = self.scale_coordinates(node.position)
            
            # Energy indicator (outer circle)
            energy_radius = self.node_radius + 4
            energy_angle = node.energy * 3.6  # Convert to degrees (0-360)
            self.canvas.create_arc(
                x - energy_radius, y - energy_radius,
                x + energy_radius, y + energy_radius,
                start=0, extent=energy_angle,
                fill='',
                outline='#4CAF50',
                width=2
            )
            
            # Node circle
            color = self.colors['malicious_node'] if node.is_malicious else self.colors['normal_node']
            if node_id == self.selected_node:
                color = self.colors['selected_node']
                
            self.canvas.create_oval(
                x - self.node_radius, y - self.node_radius,
                x + self.node_radius, y + self.node_radius,
                fill=color,
                outline='white',
                width=2
            )
            
            # Node ID
            self.canvas.create_text(
                x, y,
                text=str(node_id),
                fill=self.colors['text'],
                font=('Helvetica', 9, 'bold')
            )
            
            # Reputation indicator (if not malicious)
            if not node.is_malicious:
                rep_radius = self.node_radius + 8
                rep_angle = node.reputation * 360
                self.canvas.create_arc(
                    x - rep_radius, y - rep_radius,
                    x + rep_radius, y + rep_radius,
                    start=0, extent=rep_angle,
                    fill='',
                    outline='#2196F3',
                    width=2
                )
    
    def scale_coordinates(self, pos):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        x = (pos[0] / 100.0) * (canvas_width - 40) + 20
        y = (pos[1] / 100.0) * (canvas_height - 40) + 20
        
        return x, y
    
    def update_speed(self, value):
        self.animation_speed = value
    
    def add_node(self):
        node_id = len(self.manet.nodes)
        self.manet.nodes[node_id] = Node(node_id)
        self.manet.update_topology()
        self.update_statistics()
    
    def remove_node(self):
        if not self.manet.nodes:
            messagebox.showwarning("Error", "No nodes to remove.")
            return
        
        # Remove the last node
        node_id = len(self.manet.nodes) - 1
        del self.manet.nodes[node_id]
        
        # Recompute the network topology
        self.manet.update_topology()
        
        # Update the statistics and UI
        self.update_statistics()
        self.update_visualization()

    def update_statistics(self):
        total_nodes = len(self.manet.nodes)
        malicious_nodes = sum(1 for node in self.manet.nodes.values() if node.is_malicious)
        success_rate = (self.success_count / self.total_routes) * 100 if self.total_routes > 0 else 0
        active_routes = len(self.packet_routes)
        avg_energy = sum(node.energy for node in self.manet.nodes.values()) / total_nodes if total_nodes > 0 else 0
        
        self.stats_labels['nodes'].configure(text=str(total_nodes))
        self.stats_labels['malicious'].configure(text=str(malicious_nodes))
        self.stats_labels['success_rate'].configure(text=f"{success_rate:.2f}%")
        self.stats_labels['active_routes'].configure(text=str(active_routes))
        self.stats_labels['avg_energy'].configure(text=f"{avg_energy:.2f}")
    
    def on_canvas_click(self, event):
        x, y = event.x, event.y
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Convert canvas coordinates to the network position
        pos_x = (x - 20) / (canvas_width - 40) * 100
        pos_y = (y - 20) / (canvas_height - 40) * 100
        
        # Find the closest node to the clicked position
        closest_node = None
        min_distance = float('inf')
        for node in self.manet.nodes.values():
            dist = math.sqrt((node.position[0] - pos_x) ** 2 + (node.position[1] - pos_y) ** 2)
            if dist < min_distance:
                min_distance = dist
                closest_node = node
        
        if closest_node:
            self.selected_node = closest_node.node_id
            self.update_node_info()
            self.update_visualization()

    def update_node_info(self):
        if self.selected_node is None:
            return
        
        node = self.manet.nodes[self.selected_node]
        
        self.node_info_labels["ID"].configure(text=str(node.node_id))
        self.node_info_labels["Position"].configure(text=f"({node.position[0]:.2f}, {node.position[1]:.2f})")
        self.node_info_labels["Energy"].configure(text=f"{node.energy:.2f}")
        self.node_info_labels["Reputation"].configure(text=f"{node.reputation:.2f}")
        self.node_info_labels["Neighbors"].configure(text=", ".join(map(str, node.neighbors)))

if __name__ == "__main__":
    app = EnhancedMANETVisualizer()
    app.mainloop()
