import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import math

class SuffixTreeNode:
    def __init__(self):
        self.children = {}
        self.start = -1
        self.end = -1
        self.suffix_index = -1
        self.suffix_link = None
        
class SuffixTree:
    def __init__(self, text):
        self.text = text + "$"  # Agregar terminador
        self.root = SuffixTreeNode()
        self.build_suffix_tree()
        
    def build_suffix_tree(self):
        """Construcción simplificada del suffix tree (algoritmo básico)"""
        n = len(self.text)
        
        # Para cada sufijo
        for i in range(n):
            current = self.root
            j = i
            
            while j < n:
                char = self.text[j]
                
                if char not in current.children:
                    # Crear nueva rama
                    new_node = SuffixTreeNode()
                    new_node.start = j
                    new_node.end = n - 1
                    new_node.suffix_index = i
                    current.children[char] = new_node
                    break
                else:
                    # Navegar por rama existente
                    child = current.children[char]
                    edge_length = child.end - child.start + 1
                    
                    # Comparar caracteres en la arista
                    k = 0
                    while k < edge_length and j + k < n and self.text[child.start + k] == self.text[j + k]:
                        k += 1
                    
                    if k == edge_length:
                        # Toda la arista coincide, continuar
                        current = child
                        j += k
                    else:
                        # Dividir la arista
                        split_node = SuffixTreeNode()
                        split_node.start = child.start
                        split_node.end = child.start + k - 1
                        
                        # Actualizar el nodo hijo
                        child.start += k
                        split_node.children[self.text[child.start]] = child
                        
                        # Crear nueva rama
                        new_node = SuffixTreeNode()
                        new_node.start = j + k
                        new_node.end = n - 1
                        new_node.suffix_index = i
                        split_node.children[self.text[j + k]] = new_node
                        
                        # Actualizar padre
                        current.children[char] = split_node
                        break
    
    def get_edge_label(self, node):
        """Obtener la etiqueta de la arista"""
        if node.start == -1:
            return ""
        return self.text[node.start:node.end + 1]

class SuffixTreeGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Visualizador de Suffix Tree")
        self.master.geometry("1000x700")
        
        self.suffix_tree = None
        self.canvas_width = 800
        self.canvas_height = 600  # Más altura
        self.node_positions = {}
        
        self.setup_ui()
        
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Entrada de texto
        ttk.Label(main_frame, text="Texto de entrada:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.text_entry = ttk.Entry(main_frame, width=40, font=("Arial", 12))
        self.text_entry.grid(row=0, column=1, padx=5, pady=5)
        self.text_entry.insert(0, "banana")
        
        # Botón para generar
        ttk.Button(main_frame, text="Generar Suffix Tree", 
                  command=self.generate_tree).grid(row=0, column=2, padx=5, pady=5)
        
        # Canvas para el árbol
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.grid(row=1, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.canvas = tk.Canvas(canvas_frame, width=self.canvas_width, height=self.canvas_height, 
                               bg="white", scrollregion=(0, 0, 2000, 1000))  # Área más grande
        
        # Scrollbars
        h_scroll = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        v_scroll = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
        
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        h_scroll.grid(row=1, column=0, sticky=(tk.W, tk.E))
        v_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Información del árbol
        info_frame = ttk.LabelFrame(main_frame, text="Información", padding="5")
        info_frame.grid(row=2, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))
        
        self.info_text = scrolledtext.ScrolledText(info_frame, height=6, width=80)
        self.info_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar redimensionamiento
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)
        info_frame.columnconfigure(0, weight=1)
        
        # Generar árbol inicial
        self.generate_tree()
        
    def generate_tree(self):
        text = self.text_entry.get().strip()
        if not text:
            messagebox.showwarning("Advertencia", "Por favor ingresa un texto")
            return
            
        try:
            self.suffix_tree = SuffixTree(text)
            self.draw_tree()
            self.show_info(text)
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar el árbol: {str(e)}")
    
    def calculate_positions(self, node, x, y, level=0, parent_x=None):
        """Calcular posiciones de los nodos recursivamente"""
        self.node_positions[id(node)] = (x, y)
        
        if not node.children:
            return x + 150  # Más espacio entre hojas
        
        # Calcular ancho necesario para los hijos
        child_count = len(node.children)
        spacing = max(150, 200 // (level + 1))  # Espaciado adaptativo por nivel
        
        if child_count == 1:
            child_x = x
        else:
            total_width = (child_count - 1) * spacing
            child_x = x - total_width // 2
        
        next_x = x
        for i, (char, child) in enumerate(sorted(node.children.items())):
            child_y = y + 100  # Más espacio vertical
            next_x = self.calculate_positions(child, child_x, child_y, level + 1, x)
            child_x += spacing
            
        return max(next_x, x + child_count * spacing // 2)
    
    def draw_tree(self):
        """Dibujar el suffix tree en el canvas"""
        self.canvas.delete("all")
        self.node_positions = {}
        
        if not self.suffix_tree:
            return
        
        # Calcular posiciones
        start_x = 100  # Empezar más a la izquierda
        start_y = 50
        self.calculate_positions(self.suffix_tree.root, start_x, start_y)
        
        # Dibujar aristas primero
        self.draw_edges(self.suffix_tree.root)
        
        # Dibujar nodos
        self.draw_nodes(self.suffix_tree.root)
        
        # Actualizar scroll region con más espacio
        bbox = self.canvas.bbox("all")
        if bbox:
            self.canvas.configure(scrollregion=(bbox[0]-50, bbox[1]-50, bbox[2]+50, bbox[3]+50))
    
    def draw_edges(self, node, parent_pos=None):
        """Dibujar las aristas del árbol"""
        node_pos = self.node_positions[id(node)]
        
        if parent_pos:
            # Dibujar línea
            self.canvas.create_line(parent_pos[0], parent_pos[1], 
                                  node_pos[0], node_pos[1], 
                                  width=2, fill="black")
            
            # Dibujar etiqueta de la arista
            edge_label = self.suffix_tree.get_edge_label(node)
            if edge_label:
                # Calcular posición de la etiqueta
                mid_x = (parent_pos[0] + node_pos[0]) // 2
                mid_y = (parent_pos[1] + node_pos[1]) // 2
                
                # Ajustar posición si la etiqueta es muy larga
                if len(edge_label) > 8:
                    # Posicionar más cerca del nodo padre para etiquetas largas
                    mid_x = parent_pos[0] + (node_pos[0] - parent_pos[0]) * 0.3
                    mid_y = parent_pos[1] + (node_pos[1] - parent_pos[1]) * 0.3
                
                # Crear fondo para la etiqueta si es larga
                if len(edge_label) > 5:
                    bbox = self.canvas.create_text(mid_x, mid_y, text=edge_label, 
                                                 font=("Arial", 9, "bold"))
                    text_bbox = self.canvas.bbox(bbox)
                    self.canvas.create_rectangle(text_bbox[0]-2, text_bbox[1]-1, 
                                               text_bbox[2]+2, text_bbox[3]+1, 
                                               fill="lightyellow", outline="gray", width=1)
                    self.canvas.delete(bbox)
                
                self.canvas.create_text(mid_x, mid_y, text=edge_label, 
                                      font=("Arial", 9, "bold"), 
                                      fill="blue", tags="edge_label")
        
        # Recursivamente dibujar hijos
        for child in node.children.values():
            self.draw_edges(child, node_pos)
    
    def draw_nodes(self, node):
        """Dibujar los nodos del árbol"""
        x, y = self.node_positions[id(node)]
        
        # Determinar color del nodo
        if node.suffix_index != -1:
            # Nodo hoja
            color = "lightgreen"
            text = str(node.suffix_index)
        else:
            # Nodo interno
            color = "lightblue"
            text = ""
        
        # Dibujar círculo
        radius = 15
        self.canvas.create_oval(x - radius, y - radius, 
                              x + radius, y + radius, 
                              fill=color, outline="black", width=2)
        
        # Dibujar texto en el nodo
        if text:
            self.canvas.create_text(x, y, text=text, font=("Arial", 10, "bold"))
        
        # Recursivamente dibujar hijos
        for child in node.children.values():
            self.draw_nodes(child)
    
    def show_info(self, text):
        """Mostrar información sobre el suffix tree"""
        self.info_text.delete(1.0, tk.END)
        
        info = f"Texto: {text}\n"
        info += f"Longitud: {len(text)}\n"
        info += f"Sufijos:\n"
        
        for i in range(len(text)):
            suffix = text[i:] + "$"
            info += f"  {i}: {suffix}\n"
        
        info += f"\nLeyenda:\n"
        info += f"• Nodos azules: nodos internos\n"
        info += f"• Nodos verdes: hojas (con índice de sufijo)\n"
        info += f"• Etiquetas azules: caracteres de las aristas\n"
        
        self.info_text.insert(tk.END, info)

def main():
    root = tk.Tk()
    app = SuffixTreeGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()