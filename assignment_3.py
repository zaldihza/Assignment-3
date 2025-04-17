import heapq
import math
import time
import random

class DeliveryMap:
    def __init__(self, width, height):
        """
        Inisialisasi peta untuk layanan pengantaran makanan
        
        Args:
            width: Lebar peta
            height: Tinggi peta
        """
        self.width = width
        self.height = height
        self.grid = [['.' for _ in range(width)] for _ in range(height)]
        self.restaurants = {}
        self.customers = {}
        self.traffic = set()
        
    def add_restaurant(self, name, x, y):
        """Tambahkan restoran ke peta"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = 'R'
            self.restaurants[name] = (x, y)
            return True
        return False
    
    def add_customer(self, name, x, y):
        """Tambahkan pelanggan ke peta"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = 'C'
            self.customers[name] = (x, y)
            return True
        return False
    
    def add_traffic(self, x, y, weight=3):
        """Tambahkan area lalu lintas padat ke peta dengan bobot tertentu"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = 'T'
            self.traffic.add((x, y, weight))
            return True
        return False
    
    def add_obstacle(self, x, y):
        """Tambahkan rintangan ke peta"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = '#'
            return True
        return False
    
    def get_edge_cost(self, current, neighbor):
        """Hitung biaya perpindahan antar node"""
        x1, y1 = current
        x2, y2 = neighbor
        
        # Jika tujuan adalah area lalu lintas padat, tingkatkan biaya
        for tx, ty, weight in self.traffic:
            if x2 == tx and y2 == ty:
                return weight
        
        # Biaya default untuk jalan normal
        return 1
    
    def is_valid_position(self, x, y):
        """Periksa apakah posisi valid dan bukan obstacle"""
        return (0 <= x < self.width and 
                0 <= y < self.height and 
                self.grid[y][x] != '#')
    
    def generate_random_map(self, num_restaurants=3, num_customers=5, 
                           num_traffic=8, num_obstacles=10):
        """Generate peta acak dengan restoran, pelanggan, kemacetan, dan rintangan"""
        # Reset peta
        self.grid = [['.' for _ in range(self.width)] for _ in range(self.height)]
        self.restaurants = {}
        self.customers = {}
        self.traffic = set()
        
        # Tambahkan restoran
        for i in range(num_restaurants):
            while True:
                x, y = random.randint(0, self.width-1), random.randint(0, self.height-1)
                if self.grid[y][x] == '.':
                    self.add_restaurant(f"R{i+1}", x, y)
                    break
        
        # Tambahkan pelanggan
        for i in range(num_customers):
            while True:
                x, y = random.randint(0, self.width-1), random.randint(0, self.height-1)
                if self.grid[y][x] == '.':
                    self.add_customer(f"C{i+1}", x, y)
                    break
        
        # Tambahkan kemacetan
        for i in range(num_traffic):
            while True:
                x, y = random.randint(0, self.width-1), random.randint(0, self.height-1)
                if self.grid[y][x] == '.':
                    weight = random.randint(2, 5)  # Bobot acak untuk kemacetan
                    self.add_traffic(x, y, weight)
                    break
        
        # Tambahkan rintangan
        for i in range(num_obstacles):
            while True:
                x, y = random.randint(0, self.width-1), random.randint(0, self.height-1)
                if self.grid[y][x] == '.':
                    self.add_obstacle(x, y)
                    break
    
    def print_map(self, path=None):
        """Cetak peta dengan jalur pengantaran jika ada"""
        # Buat salinan peta untuk visualisasi
        visual_map = [row[:] for row in self.grid]
        
        # Tandai jalur dengan '+'
        if path:
            for x, y in path:
                # Jangan menimpa restoran atau pelanggan
                if visual_map[y][x] not in ['R', 'C']:
                    visual_map[y][x] = '+'
        
        # Cetak peta
        for row in visual_map:
            print(' '.join(row))

def a_star_search(delivery_map, start, goal):
    """
    Implementasi algoritma A* untuk menemukan rute pengantaran makanan
    
    Args:
        delivery_map: Objek DeliveryMap yang berisi informasi peta
        start: Tuple (x, y) posisi awal (restoran)
        goal: Tuple (x, y) posisi tujuan (pelanggan)
    
    Returns:
        path: Jalur pengantaran yang ditemukan
        visited_count: Jumlah node yang dikunjungi
        time_taken: Waktu eksekusi dalam milidetik
    """
    # Mencatat waktu mulai
    start_time = time.time()
    
    # Fungsi heuristik - menggunakan jarak Euclidean
    def heuristic(pos):
        x1, y1 = pos
        x2, y2 = goal
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    # Gerakan yang mungkin: atas, kanan, bawah, kiri
    directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
    
    # Menyiapkan struktur data
    open_set = []  # Priority queue
    closed_set = set()
    g_score = {start: 0}  # Biaya sebenarnya dari start ke node
    f_score = {start: heuristic(start)}  # Estimasi total biaya
    parent = {}  # Untuk rekonstruksi jalur
    visited_count = 0
    
    # Format: (f_score, position)
    heapq.heappush(open_set, (f_score[start], start))
    
    while open_set:
        # Mengambil node dengan f_score terkecil
        _, current = heapq.heappop(open_set)
        visited_count += 1
        
        # Jika tujuan sudah ditemukan, rekonstruksi jalur dan kembalikan hasilnya
        if current == goal:
            # Rekonstruksi jalur
            path = []
            while current in parent:
                path.append(current)
                current = parent[current]
            path.append(start)
            path.reverse()
            
            time_taken = (time.time() - start_time) * 1000  # Konversi ke milidetik
            return path, visited_count, time_taken
        
        # Tandai node saat ini sebagai sudah dikunjungi
        closed_set.add(current)
        
        # Jelajahi semua tetangga yang mungkin
        x, y = current
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            neighbor = (nx, ny)
            
            # Periksa# Periksa apakah posisi valid
            if not delivery_map.is_valid_position(nx, ny):
                continue
            
            # Jika sudah dikunjungi, lewati
            if neighbor in closed_set:
                continue
            
            # Hitung g_score baru
            tentative_g_score = g_score[current] + delivery_map.get_edge_cost(current, neighbor)
            
            # Jika kita menemukan jalur yang lebih baik ke neighbor
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                # Simpan jalur yang lebih baik
                parent[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor)
                
                # Tambahkan ke open set
                heapq.heappush(open_set, (f_score[neighbor], neighbor))
    
    # Jika tidak ada jalur yang ditemukan
    time_taken = (time.time() - start_time) * 1000  # Konversi ke milidetik
    return None, visited_count, time_taken

def greedy_best_first_search(delivery_map, start, goal):
    """
    Implementasi algoritma Greedy Best-First Search untuk menemukan rute pengantaran makanan
    
    Args:
        delivery_map: Objek DeliveryMap yang berisi informasi peta
        start: Tuple (x, y) posisi awal (restoran)
        goal: Tuple (x, y) posisi tujuan (pelanggan)
    
    Returns:
        path: Jalur pengantaran yang ditemukan
        visited_count: Jumlah node yang dikunjungi
        time_taken: Waktu eksekusi dalam milidetik
    """
    # Mencatat waktu mulai
    start_time = time.time()
    
    # Fungsi heuristik - menggunakan jarak Euclidean
    def heuristic(pos):
        x1, y1 = pos
        x2, y2 = goal
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    # Gerakan yang mungkin: atas, kanan, bawah, kiri
    directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
    
    # Menyiapkan struktur data
    open_set = []  # Priority queue
    closed_set = set()
    parent = {}  # Untuk rekonstruksi jalur
    visited_count = 0
    
    # Format: (heuristic_value, position)
    heapq.heappush(open_set, (heuristic(start), start))
    
    while open_set:
        # Mengambil node dengan heuristic value terkecil
        _, current = heapq.heappop(open_set)
        visited_count += 1
        
        # Jika tujuan sudah ditemukan, rekonstruksi jalur dan kembalikan hasilnya
        if current == goal:
            # Rekonstruksi jalur
            path = []
            while current in parent:
                path.append(current)
                current = parent[current]
            path.append(start)
            path.reverse()
            
            time_taken = (time.time() - start_time) * 1000  # Konversi ke milidetik
            return path, visited_count, time_taken
        
        # Tandai node saat ini sebagai sudah dikunjungi
        closed_set.add(current)
        
        # Jelajahi semua tetangga yang mungkin
        x, y = current
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            neighbor = (nx, ny)
            
            # Periksa apakah posisi valid
            if not delivery_map.is_valid_position(nx, ny):
                continue
            
            # Jika sudah dikunjungi, lewati
            if neighbor in closed_set:
                continue
            
            # Jika belum ada parent untuk neighbor atau ini jalur baru
            if neighbor not in parent:
                parent[neighbor] = current
                # Tambahkan ke open set
                heapq.heappush(open_set, (heuristic(neighbor), neighbor))
    
    # Jika tidak ada jalur yang ditemukan
    time_taken = (time.time() - start_time) * 1000  # Konversi ke milidetik
    return None, visited_count, time_taken

# Contoh penggunaan
if __name__ == "__main__":
    # Buat peta berukuran 15x15
    delivery_map = DeliveryMap(15, 15)
    
    # Generate peta acak
    delivery_map.generate_random_map()
    
    # Ambil restoran dan pelanggan pertama untuk simulasi
    if len(delivery_map.restaurants) > 0 and len(delivery_map.customers) > 0:
        restaurant_name = list(delivery_map.restaurants.keys())[0]
        customer_name = list(delivery_map.customers.keys())[0]
        
        restaurant_pos = delivery_map.restaurants[restaurant_name]
        customer_pos = delivery_map.customers[customer_name]
        
        print(f"Simulasi pengantaran makanan dari restoran {restaurant_name} ke pelanggan {customer_name}")
        print(f"Posisi restoran: {restaurant_pos}")
        print(f"Posisi pelanggan: {customer_pos}")
        
        # Cetak peta awal
        print("\nPeta Kota:")
        delivery_map.print_map()
        
        # Jalankan A*
        print("\nMencari rute dengan A*...")
        a_star_path, a_star_visited, a_star_time = a_star_search(delivery_map, restaurant_pos, customer_pos)
        
        if a_star_path:
            print(f"A* berhasil menemukan rute dengan {len(a_star_path)} langkah.")
            print(f"Jumlah node yang dikunjungi: {a_star_visited}")
            print(f"Waktu eksekusi: {a_star_time:.2f} ms")
            
            print("\nPeta dengan rute A*:")
            delivery_map.print_map(a_star_path)
        else:
            print("A* tidak menemukan rute.")
        
        # Jalankan GBFS
        print("\nMencari rute dengan Greedy Best-First Search...")
        gbfs_path, gbfs_visited, gbfs_time = greedy_best_first_search(delivery_map, restaurant_pos, customer_pos)
        
        if gbfs_path:
            print(f"GBFS berhasil menemukan rute dengan {len(gbfs_path)} langkah.")
            print(f"Jumlah node yang dikunjungi: {gbfs_visited}")
            print(f"Waktu eksekusi: {gbfs_time:.2f} ms")
            
            print("\nPeta dengan rute GBFS:")
            delivery_map.print_map(gbfs_path)
        else:
            print("GBFS tidak menemukan rute.")
        
        # Perbandingan hasil
        print("\nPerbandingan A* vs GBFS:")
        if a_star_path and gbfs_path:
            print(f"Panjang rute A*: {len(a_star_path)} langkah")
            print(f"Panjang rute GBFS: {len(gbfs_path)} langkah")
            print(f"Node yang dikunjungi A*: {a_star_visited}")
            print(f"Node yang dikunjungi GBFS: {gbfs_visited}")
            print(f"Waktu eksekusi A*: {a_star_time:.2f} ms")
            print(f"Waktu eksekusi GBFS: {gbfs_time:.2f} ms")
    else:
        print("Tidak ada restoran atau pelanggan di peta!")