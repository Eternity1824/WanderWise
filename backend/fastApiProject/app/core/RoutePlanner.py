class RoutePlanner:
    """
    路径规划类，用于规划访问所有地点的最佳路径
    使用贪心算法（最近邻算法）来解决类似旅行商问题(TSP)
    """

    def __init__(self, location_coordinates):
        """
        初始化路径规划器

        参数:
        location_coordinates -- 包含地点信息的列表，每个元素需包含name, latitude, longitude字段
        """
        self.locations = location_coordinates
        self.num_locations = len(location_coordinates)

    def calculate_distance(self, loc1, loc2):
        """
        计算两个地点之间的欧氏距离

        参数:
        loc1, loc2 -- 两个地点字典，包含latitude和longitude字段

        返回:
        两点间的欧氏距离
        """
        lat1, lon1 = loc1['latitude'], loc1['longitude']
        lat2, lon2 = loc2['latitude'], loc2['longitude']

        # 使用欧氏距离作为简化计算
        # 实际应用中可能需要使用哈弗辛公式(Haversine formula)计算实际地球表面距离
        return ((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2) ** 0.5

    def find_corner_point(self, corner_type):
        """
        寻找指定角落的点

        参数:
        corner_type -- 角落类型: 'southwest', 'northwest', 'southeast', 'northeast'

        返回:
        角落点的索引
        """
        if not self.locations:
            return None

        corner_idx = 0

        if corner_type == 'southwest':
            # 寻找最西南角的点 (最小经度和最小纬度)
            for i in range(1, self.num_locations):
                if (self.locations[i]['longitude'] < self.locations[corner_idx]['longitude'] or
                        (self.locations[i]['longitude'] == self.locations[corner_idx]['longitude'] and
                         self.locations[i]['latitude'] < self.locations[corner_idx]['latitude'])):
                    corner_idx = i

        elif corner_type == 'northwest':
            # 寻找最西北角的点 (最小经度和最大纬度)
            for i in range(1, self.num_locations):
                if (self.locations[i]['longitude'] < self.locations[corner_idx]['longitude'] or
                        (self.locations[i]['longitude'] == self.locations[corner_idx]['longitude'] and
                         self.locations[i]['latitude'] > self.locations[corner_idx]['latitude'])):
                    corner_idx = i

        elif corner_type == 'southeast':
            # 寻找最东南角的点 (最大经度和最小纬度)
            for i in range(1, self.num_locations):
                if (self.locations[i]['longitude'] > self.locations[corner_idx]['longitude'] or
                        (self.locations[i]['longitude'] == self.locations[corner_idx]['longitude'] and
                         self.locations[i]['latitude'] < self.locations[corner_idx]['latitude'])):
                    corner_idx = i

        elif corner_type == 'northeast':
            # 寻找最东北角的点 (最大经度和最大纬度)
            for i in range(1, self.num_locations):
                if (self.locations[i]['longitude'] > self.locations[corner_idx]['longitude'] or
                        (self.locations[i]['longitude'] == self.locations[corner_idx]['longitude'] and
                         self.locations[i]['latitude'] > self.locations[corner_idx]['latitude'])):
                    corner_idx = i

        return corner_idx

    def plan_route(self, start_corner='southwest'):
        """
        规划从指定角落出发的路径

        参数:
        start_corner -- 起始角落: 'southwest', 'northwest', 'southeast', 'northeast'

        返回:
        排序后的地点列表
        """
        if self.num_locations <= 1:
            return self.locations

        # 寻找起始点
        start_idx = self.find_corner_point(start_corner)

        # 初始化路径和未访问的点
        route = [self.locations[start_idx]]
        unvisited = self.locations.copy()
        unvisited.pop(start_idx)

        current_location = route[0]

        # 贪心算法：每次选择最近的下一个点
        while unvisited:
            # 寻找距离当前位置最近的点
            nearest_idx = 0
            min_distance = float('inf')

            for i, location in enumerate(unvisited):
                distance = self.calculate_distance(current_location, location)
                if distance < min_distance:
                    min_distance = distance
                    nearest_idx = i

            # 将最近点添加到路径中
            next_location = unvisited.pop(nearest_idx)
            route.append(next_location)
            current_location = next_location

        return route

    def optimize_route(self, method='2opt'):
        """
        优化路径（可选功能）

        参数:
        method -- 优化方法，当前支持'2opt'

        返回:
        优化后的路径列表
        """
        # 此处可以实现更复杂的路径优化算法，如2-opt, 3-opt等
        # 目前仅作为扩展功能的占位符

        # 如果需要实现2-opt优化，可以在此处添加

        return self.plan_route()
