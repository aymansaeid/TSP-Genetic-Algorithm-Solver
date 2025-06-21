import math
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import networkx as nx
import time
import itertools # <<< YENİ: Kombinasyonları kolayca oluşturmak için eklendi

# --- Varsayılan Genetik Algoritma Parametreleri ---
# Bu değerler, doğrudan bir deneme yapılmadığında veya tek seferlik çalıştırmada kullanılabilir.
DEFAULT_POPULATION_SIZE = 300
DEFAULT_MAX_GENERATIONS = 1000 # <<< DEĞİŞİKLİK: Ayarlama sırasında daha kısa tutulabilir
DEFAULT_CROSSOVER_RATE = 0.65
DEFAULT_MUTATION_RATE = 0.1
DEFAULT_TOURNAMENT_K = 15
DEFAULT_ELITE_RATE = 0.1 # <<< DEĞİŞİKLİK: Boyut yerine oran olarak tanımlamak daha esnektir

# Global değişken animasyon nesnesini tutmak için
ga_animation_object = None

# --- Yardımcı Fonksiyonlar ve Dosya Okuma ---
# (Bu fonksiyonlarda değişiklik yapmaya gerek yok, orijinal haliyle kalabilirler)
def calculate_distance(city1_coords, city2_coords):
    return math.sqrt((city1_coords[0] - city2_coords[0])**2 + \
                     (city1_coords[1] - city2_coords[1])**2)

def total_distance(tour, cities_coords):
    dist = 0
    num_cities = len(tour)
    if num_cities == 0: return 0
    for i in range(num_cities):
        from_city_idx = tour[i]
        to_city_idx = tour[(i + 1) % num_cities]
        dist += calculate_distance(cities_coords[from_city_idx], \
                                   cities_coords[to_city_idx])
    return dist

def read_tsp_file(file_path):
    cities_coords = {}
    try:
        with open(file_path, 'r') as f:
            num_cities_line = f.readline().strip()
            num_cities = int(num_cities_line.split()[-1])
            for i in range(num_cities):
                line_content = f.readline().strip().split()
                cities_coords[i] = (float(line_content[-2]), float(line_content[-1]))
    except Exception as e:
        print(f"Dosya okunurken bir hata oluştu: {e}")
        return None
    return cities_coords

# --- Genetik Algoritma Komponentleri ---
# (Bu fonksiyonlarda da değişiklik yapmaya gerek yok)
def create_individual(num_cities):
    individual = list(range(num_cities))
    random.shuffle(individual)
    return individual

def create_initial_population(num_cities, population_size):
    return [create_individual(num_cities) for _ in range(population_size)]

def tournament_selection(population, fitness_scores, k):
    tournament_contenders_indices = random.sample(range(len(population)), k)
    winner_index = min(tournament_contenders_indices, key=lambda i: fitness_scores[i])
    return population[winner_index]

def order_crossover_ox1(parent1, parent2):
    size = len(parent1)
    child1, child2 = [-1]*size, [-1]*size
    start, end = sorted(random.sample(range(size), 2))
    child1[start:end+1] = parent1[start:end+1]
    p2_idx = (end + 1) % size
    c1_idx = (end + 1) % size
    while -1 in child1:
        gene_from_p2 = parent2[p2_idx]
        if gene_from_p2 not in child1:
            child1[c1_idx] = gene_from_p2
            c1_idx = (c1_idx + 1) % size
        p2_idx = (p2_idx + 1) % size
    child2[start:end+1] = parent2[start:end+1]
    p1_idx = (end + 1) % size
    c2_idx = (end + 1) % size
    while -1 in child2:
        gene_from_p1 = parent1[p1_idx]
        if gene_from_p1 not in child2:
            child2[c2_idx] = gene_from_p1
            c2_idx = (c2_idx + 1) % size
        p1_idx = (p1_idx + 1) % size
    return child1, child2

def inversion_mutation(individual, mutation_rate):
    if random.random() < mutation_rate:
        size = len(individual)
        idx1, idx2 = sorted(random.sample(range(size), 2))
        sub_tour = individual[idx1:idx2+1]
        sub_tour.reverse()
        individual[idx1:idx2+1] = sub_tour
    return individual

# --- Görselleştirme Fonksiyonu ---
# (Bu fonksiyonda da değişiklik yapmaya gerek yok)
def plot_results_combined_animated(best_tour_overall, cities_coords, convergence_data, title_suffix=""):
    global ga_animation_object
    if not cities_coords: return
    fig, axs = plt.subplots(1, 2, figsize=(18, 8))
    # ... (Görselleştirme kodunuzun geri kalanı buraya gelecek, değişiklik yok)
    # Kodun kısalığı için bu bölümü daraltıyorum, orijinal kodunuzdaki ile aynı.
    ax_convergence = axs[0]
    if convergence_data:
        generations_list = [data[0] for data in convergence_data]
        best_fitness_list = [data[1] for data in convergence_data]
        ax_convergence.plot(generations_list, best_fitness_list, label="En İyi Mesafe (Min)")
        ax_convergence.set_xlabel("Jenerasyon")
        ax_convergence.set_ylabel("Toplam Mesafe")
        ax_convergence.set_title(f"Yakınsama Grafiği {title_suffix}")
        ax_convergence.legend()
        ax_convergence.grid(True)
    ax_tour_animation = axs[1]
    G_nx = nx.Graph()
    pos = {city_id: coords for city_id, coords in cities_coords.items()}
    G_nx.add_nodes_from(pos.keys())
    nx.draw(G_nx, pos, ax=ax_tour_animation, with_labels=True, node_color='lightblue', node_size=400)
    if best_tour_overall:
        tour_edges = [(best_tour_overall[i], best_tour_overall[(i + 1) % len(best_tour_overall)]) for i in range(len(best_tour_overall))]
        nx.draw_networkx_edges(G_nx, pos, edgelist=tour_edges, ax=ax_tour_animation, edge_color='red', width=2)
        dist = total_distance(best_tour_overall, cities_coords)
        ax_tour_animation.set_title(f"En İyi Tur {title_suffix}\nMesafe: {dist:.1f}")
    plt.tight_layout()


# --- Ana Genetik Algoritma Fonksiyonu (YENİDEN DÜZENLENDİ) ---
# <<< DEĞİŞİKLİK: Fonksiyon artık parametreleri argüman olarak alıyor.
def genetic_algorithm_tsp(cities_coords, population_size, max_generations, crossover_rate, mutation_rate, tournament_k, elite_rate, file_name_for_title="", show_plot=False, verbose=True):
    if not cities_coords: return None, float('inf'), 0
    num_cities = len(cities_coords)
    if num_cities == 0: return None, float('inf'), 0

    # <<< DEĞİŞİKLİK: Elitizm boyutu artık orana göre hesaplanıyor.
    elite_size = int(population_size * elite_rate)

    population = create_initial_population(num_cities, population_size)
    best_tour_overall = None
    best_distance_overall = float('inf')
    convergence_data = []
    start_time = time.time()

    for generation in range(max_generations):
        fitness_scores = [total_distance(tour, cities_coords) for tour in population]
        sorted_population_indices = sorted(range(len(population)), key=lambda k: fitness_scores[k])
        
        current_best_distance_gen = fitness_scores[sorted_population_indices[0]]
        if current_best_distance_gen < best_distance_overall:
            best_distance_overall = current_best_distance_gen
            best_tour_overall = list(population[sorted_population_indices[0]])

        avg_distance_gen = sum(fitness_scores) / len(fitness_scores)
        convergence_data.append((generation, current_best_distance_gen, avg_distance_gen))

        # <<< DEĞİŞİKLİK: verbose bayrağı ile konsol çıktısını kontrol etme
        if verbose and (generation + 1) % 100 == 0:
            print(f"Jenerasyon {generation+1}/{max_generations} - En İyi: {best_distance_overall:.2f}, Ort: {avg_distance_gen:.2f}")

        new_population = [population[i] for i in sorted_population_indices[:elite_size]]
        
        num_children_needed = population_size - elite_size
        children = []
        for _ in range(num_children_needed // 2):
            parent1 = tournament_selection(population, fitness_scores, tournament_k)
            parent2 = tournament_selection(population, fitness_scores, tournament_k)
            child1, child2 = parent1, parent2
            if random.random() < crossover_rate:
                child1, child2 = order_crossover_ox1(parent1, parent2)
            children.append(inversion_mutation(list(child1), mutation_rate))
            children.append(inversion_mutation(list(child2), mutation_rate))

        new_population.extend(children)
        population = new_population

    end_time = time.time()
    computation_time = end_time - start_time

    if verbose:
        print(f"\n--- Algoritma Tamamlandı ({file_name_for_title}) ---")
        print(f"Toplam Hesaplama Süresi: {computation_time:.2f} saniye")
        print(f"Bulunan En İyi Mesafe: {best_distance_overall:.1f}")

    # <<< DEĞİŞİKLİK: Görselleştirme artık show_plot bayrağı ile kontrol ediliyor.
    if show_plot:
        # Görselleştirme için orijinal fonksiyonunuzu çağırabilirsiniz.
        # Basitlik adına burada sadeleştirilmiş bir versiyon kullanıyorum.
        plot_results_combined_animated(best_tour_overall, cities_coords, convergence_data, title_suffix=f"({file_name_for_title})")
        plt.show()

    return best_tour_overall, best_distance_overall, computation_time


# --- YENİ PARAMETRE AYARLAMA (TUNING) FONKSİYONU ---
def parameter_tuning_experiment(cities_coords, problem_name):
    """
    Farklı GA parametrelerini sistematik olarak dener ve en iyisini bulur.
    """
    
    param_grid = {
        'population_size': [100, 200],
        'max_generations': [500], # Ayarlama sırasında daha kısa tutmak mantıklıdır
        'crossover_rate': [0.6, 0.8],
        'mutation_rate': [0.05, 0.15],
        'tournament_k': [10, 20],
        'elite_rate': [0.1]
    }

    # Tüm olası parametre kombinasyonlarını oluştur
    keys, values = zip(*param_grid.items())
    param_combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]

    print(f"--- Parametre Ayarlama Deneyi Başlatılıyor ---")
    print(f"Problem: {problem_name}")
    print(f"Toplam {len(param_combinations)} farklı parametre kombinasyonu denenecek.\n")

    results = []
    best_overall_result = {
        'params': None,
        'distance': float('inf'),
        'tour': None,
        'time': 0
    }

    # Her bir kombinasyonu dene
    for i, params in enumerate(param_combinations):
        print(f"--> Deneme {i+1}/{len(param_combinations)}: {params}")
        
        # GA'yı çalıştır, ancak bu sırada grafik gösterme (show_plot=False) ve
        # jenerasyon detaylarını basma (verbose=False)
        tour, distance, comp_time = genetic_algorithm_tsp(
            cities_coords,
            population_size=params['population_size'],
            max_generations=params['max_generations'],
            crossover_rate=params['crossover_rate'],
            mutation_rate=params['mutation_rate'],
            tournament_k=params['tournament_k'],
            elite_rate=params['elite_rate'],
            file_name_for_title=problem_name,
            show_plot=False,  # Ayarlama sırasında plot gösterme
            verbose=False      # Ayarlama sırasında jenerasyonları yazdırma
        )
        
        print(f"    Sonuç: Mesafe = {distance:.2f}, Süre = {comp_time:.2f}s")

        # Sonuçları kaydet
        current_result = {'params': params, 'distance': distance, 'time': comp_time}
        results.append(current_result)

        # Şimdiye kadarki en iyi sonucu güncelle
        if distance < best_overall_result['distance']:
            best_overall_result['distance'] = distance
            best_overall_result['tour'] = tour
            best_overall_result['params'] = params
            best_overall_result['time'] = comp_time
            print("    *** Yeni en iyi sonuç bulundu! ***")
        
        print("-" * 30)

    # --- Sonuçların Raporlanması ---
    print("\n\n--- Parametre Ayarlama Sonuçları ---")
    # Tüm sonuçları mesafeye göre sırala ve göster
    results.sort(key=lambda x: x['distance'])
    print("Sıra | Mesafe     | Süre(s) | Parametreler")
    print("-----|------------|---------|------------------------------------")
    for idx, res in enumerate(results[:10]): # En iyi 10 sonucu göster
        print(f"{idx+1:<5}| {res['distance']:<10.2f} | {res['time']:<7.2f} | {res['params']}")

    print("\n\n--- EN İYİ PERFORMANS GÖSTEREN PARAMETRELER ---")
    print(f"En İyi Mesafe: {best_overall_result['distance']:.2f}")
    print(f"Hesaplama Süresi: {best_overall_result['time']:.2f}s")
    print("Parametreler:")
    for key, value in best_overall_result['params'].items():
        print(f"  - {key}: {value}")

    print("\n--- En İyi Parametrelerle Final Çalıştırması ve Görselleştirme ---")
    # En iyi bulunan parametrelerle GA'yı son bir kez daha çalıştır,
    # bu sefer görselleştirmeyi ve detaylı çıktıyı açarak.
    final_params = best_overall_result['params']
    genetic_algorithm_tsp(
        cities_coords,
        population_size=final_params['population_size'],
        max_generations=10000, # Final çalıştırması için jenerasyonu artırabiliriz
        crossover_rate=final_params['crossover_rate'],
        mutation_rate=final_params['mutation_rate'],
        tournament_k=final_params['tournament_k'],
        elite_rate=final_params['elite_rate'],
        file_name_for_title=f"{problem_name} (En İyi Ayar)",
        show_plot=True,
        verbose=True
    )


# --- Ana Çalıştırma Bloğu (YENİDEN DÜZENLENDİ) ---
if __name__ == "__main__":
    file_path = input("Lütfen TSP dosyasının yolunu girin (örn: tsp_5_1.txt): ")
    cities = read_tsp_file(file_path)
    if cities:
        problem_name = file_path.split('/')[-1].split('.')[0]
        
        # <<< YENİ: Parametre ayarlama fonksiyonunu çağırıyoruz.
        parameter_tuning_experiment(cities, problem_name)
    else:
        print("Geçerli şehir verisi okunamadı. Program sonlandırılıyor.")