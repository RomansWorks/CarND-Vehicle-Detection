import numpy as np

class WindowSlider():
    
    def __init__(self, 
                     x_start_stop=[None, None], 
                     y_start_stop=[None, None], 
                     xy_window=(64, 64), 
                     xy_overlap=(0.5, 0.5)):
        assert(x_start_stop[0] is not None)
        assert(x_start_stop[1] is not None)
        assert(y_start_stop[0] is not None)
        assert(y_start_stop[1] is not None)
        assert(xy_window[0] > 0)
        assert(xy_window[0] > 0)
        assert(xy_overlap[0] > 0 and xy_overlap[0] < 1)
        assert(xy_overlap[1] > 0 and xy_overlap[1] < 1)

        # Compute the span of the region to be searched    
        xspan = x_start_stop[1] - x_start_stop[0]
        yspan = y_start_stop[1] - y_start_stop[0]
        # Compute the number of pixels per step in x/y
        nx_pix_per_step = np.int(xy_window[0]*(1 - xy_overlap[0]))
        ny_pix_per_step = np.int(xy_window[1]*(1 - xy_overlap[1]))
        # Compute the number of windows in x/y
        nx_buffer = np.int(xy_window[0]*(xy_overlap[0]))
        ny_buffer = np.int(xy_window[1]*(xy_overlap[1]))
        nx_windows = np.int((xspan-nx_buffer)/nx_pix_per_step) 
        ny_windows = np.int((yspan-ny_buffer)/ny_pix_per_step) 
        # Initialize a list to append window positions to
        window_list = []
        # Loop through finding x and y window positions
        for ys in range(ny_windows):
            for xs in range(nx_windows):
                # Calculate window position
                startx = xs*nx_pix_per_step + x_start_stop[0]
                endx = startx + xy_window[0]
                starty = ys*ny_pix_per_step + y_start_stop[0]
                endy = starty + xy_window[1]

                # Append window position to list
                window_list.append(((startx, starty), (endx, endy)))
        
        # Store the window list
        self.window_list = window_list

        
    def get_all_windows(self):
        return self.window_list
    
    def windows_to_heatmap(image_shape, positive_windows):
        heatmap = np.zeros(image_shape)
        for window in positive_windows:
            heatmap[window[0][1]:window[1][1], window[0][0]:window[1][0]] += 1
        return heatmap

    def get_labeled_bboxes(labels):
        bboxes = []
        # Iterate through all detected labels
        for detection_idx in range(1, labels[1]+1):
            # Find pixels with each label value
            nonzero = (labels[0] == detection_idx).nonzero()
            # Identify x and y values of those pixels
            nonzeroy = np.array(nonzero[0])
            nonzerox = np.array(nonzero[1])
            # Define a bounding box based on min/max x and y
            bbox = ((np.min(nonzerox), np.min(nonzeroy)), (np.max(nonzerox), np.max(nonzeroy)))
            bboxes.append(bbox)
        return bboxes
    
    
class PartitioningWindowSlider(WindowSlider):
    def __init__(self, 
             x_start_stop=[None, None], 
             y_start_stop=[None, None], 
             xy_window=(64, 64), 
             xy_overlap=(0.5, 0.5),
             n_partitions=1
            ):
        super().__init__(x_start_stop, y_start_stop, xy_window, xy_overlap)
        assert(n_partitions > 0)
        self.n_partitions = n_partitions
                
        # Partition
        self.partition_list = PartitioningWindowSlider.__partition_search_windows(self.window_list, n_partitions)
        
    def get_partition(self, idx):
        return self.partition_list[idx]
        
    def __partition_search_windows(bboxes, n_partitions):
        # We care about nearby and overlapping windows since these give us the heat in the heatmap
        # We therefore need an overlap when partitioning, such that edges of partitions are rescanned in the next partition
        # First, we find min x, y and max x, y
        min_x = min_y = max_x = max_y = 0
        for bbox in bboxes:
            if bbox[0][0] < min_x:
                min_x = bbox[0][0]
            if bbox[0][1] < min_y:
                min_y = bbox[0][1]
            if bbox[1][0] > max_x:
                max_x = bbox[1][0]
            if bbox[1][1] > max_y:
                max_y = bbox[1][1]

        # Next we partition vertically for n partitions.
        # For an overlap of 50%, we move ahead up to 1.5 steps
        overlap_rate=0.5
        dx = (max_x - min_x)/(n_partitions)
        partitioned_bboxes = []
        for step in range(0, n_partitions):
            partitioned_bboxes.append([])
            partition_min_x = min_x + step*dx
            partition_max_x = min_x + (step+1+overlap_rate)*dx
            partition_bboxes = []
            for bbox in bboxes:
                bbox_left_x = bbox[0][0]
                if bbox_left_x >= partition_min_x and bbox_left_x <= partition_max_x:
                    partitioned_bboxes[step].append(bbox)

        return partitioned_bboxes

class PartitioningWindowSliderGroup():
    
    # Example search ranges:
    #WINDOW_SEARCH_RANGES = [
    #     {'window_size': (192,192), 'x_start_stop': [0, 1280], 'y_start_stop': [360, 740], 'xy_overlap':(0.85, 0.85)},
    #     {'window_size': (160,160), 'x_start_stop': [0, 1280], 'y_start_stop': [360, 740], 'xy_overlap':(0.85, 0.85)},
    #     {'window_size': (128,128), 'x_start_stop': [0, 1280], 'y_start_stop': [360, 700], 'xy_overlap':(0.85, 0.85)},
    #     {'window_size': (96,96), 'x_start_stop': [200, 1200], 'y_start_stop': [360, 550], 'xy_overlap':(0.85, 0.85)},
    #     {'window_size': (64,64), 'x_start_stop': [200, 1200], 'y_start_stop': [360, 500], 'xy_overlap':(0.85, 0.85)},
    #]

    
    
    def __init__(self, search_ranges, n_partitions=1):
        self.n_partitions = n_partitions
        self.sliders = []
        for search_range in search_ranges:
            slider = PartitioningWindowSlider( 
                x_start_stop=search_range['x_start_stop'], 
                y_start_stop=search_range['y_start_stop'], 
                xy_window=search_range['window_size'],
                xy_overlap=search_range['xy_overlap'], 
                n_partitions=n_partitions)
            self.sliders.append(slider)
        self.precalculated_partitions = self.__precalculate_partitions()
            
    def __precalculate_partitions(self):
        # Calculate partitions
        partitions_bboxes = []
        for partition_idx in range(0,self.n_partitions):
            partition_bboxes = []
            for slider in self.sliders:
                windows = slider.get_partition(partition_idx)
                partition_bboxes.extend(windows)
            partitions_bboxes.append(partition_bboxes)   
        return partitions_bboxes
    
    def get_windows_for_partition(self, partition_idx):
        assert(partition_idx < self.n_partitions)
        return self.precalculated_partitions[partition_idx]

    
#WINDOW_SEARCH_RANGES = [
#     {'window_size': (192,192), 'x_start_stop': [0, 1280], 'y_start_stop': [360, 740], 'xy_overlap':(0.85, 0.85)},
#     {'window_size': (160,160), 'x_start_stop': [0, 1280], 'y_start_stop': [360, 740], 'xy_overlap':(0.85, 0.85)},
#     {'window_size': (128,128), 'x_start_stop': [0, 1280], 'y_start_stop': [360, 700], 'xy_overlap':(0.85, 0.85)},
#     {'window_size': (96,96), 'x_start_stop': [200, 1200], 'y_start_stop': [360, 550], 'xy_overlap':(0.85, 0.85)},
#     {'window_size': (64,64), 'x_start_stop': [200, 1200], 'y_start_stop': [360, 500], 'xy_overlap':(0.85, 0.85)},
#]
#
#
# PartitioningWindowSliderGroup(WINDOW_SEARCH_RANGES, 32)

    