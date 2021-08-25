import os
import time
import common  # 여기서 Profile 클래스 인스턴스도 하나 생성함
from datetime import datetime
import matplotlib.pyplot as plt
import random as rnd

"""
0 : 2021-08-24-18-23-51-547834-FC-111.log
1 : 2021-08-24-18-34-15-620348-FC-111.log
2 : 2021-08-24-18-39-01-978185-FC-111.log
<min 값을 취한 결과>
list_fc_111_min = [0.061337, 0.062442, 0.077007, 0.06244, 0.076932, 
                    0.062398, 0.06242, 0.076928, 0.061069, 0.061383,
                     0.078007, 0.08021, 0.061399, 0.06114, 0.063035, 
                     0.092573, 0.092626, 0.09381, 0.077658, 0.062498, 
                     0.078124, 0.061565, 0.045407, 0.062364, 0.076982, 
                     0.061401, 0.07706, 0.062923, 0.060974, 0.062546, 
                     0.062497, 0.0614, 0.092279, 0.061408, 0.061418, 
                     0.078078, 0.077029, 0.077045, 0.076998, 0.062529, 
                     0.062408, 0.077009, 0.085933, 0.063623, 0.061574, 
                     0.077976, 0.078835, 0.07799, 0.060966, 0.13944, 
                     0.187647, 0.158812, 0.126163, 0.170783, 0.187475, 
                     0.092277, 0.109415, 0.127974, 0.171966, 0.170344, 
                     0.092636, 0.15622, 0.108305, 0.077035, 0.21837, 
                     0.108678, 0.108277, 0.0933, 0.09365, 0.108285, 
                     0.202039, 0.095694, 0.092581, 0.092656, 0.093787, 
                     0.109386, 0.110854, 0.126032, 0.093734, 0.108315, 
                     0.109452, 0.108179, 0.109798, 0.109276, 0.108236, 
                     0.094284, 0.108255, 0.155095, 0.10827, 0.108311, 
                     0.108261, 0.187412, 0.092612, 0.109245, 0.10931, 
                     0.124692, 0.186341, 0.093746, 0.108193, 0.108722, 
                     0.139534, 0.108243, 0.109008, 0.093699, 0.092318, 
                     0.156456, 0.108278, 0.140555, 0.219034, 0.108271, 
                     0.20305, 0.108236, 0.109424, 0.140648, 0.093667, 
                     0.140654, 0.139475, 0.109292, 0.092594, 0.092689, 
                     0.093565, 0.093581, 0.108287, 0.186429, 0.108297, 
                     0.092656, 0.186367, 0.109257, 0.092628, 0.109385, 
                     0.108189, 0.108182, 0.13954, 0.109396, 0.10822, 
                     0.078727, 0.092657, 0.094743, 0.108225, 0.158085, 
                     0.109283, 0.094532, 0.092657, 0.1265, 0.108287, 
                     0.108269, 0.110107, 0.108277, 0.092649, 0.108227, 
                     0.109284, 0.171918, 0.109413, 0.094474, 0.109234, 
                     0.094284, 0.155073, 0.094145, 0.079228, 0.156199, 
                     0.077052, 0.078091, 0.061381, 0.155268, 0.062924, 
                     0.078844, 0.062501, 0.061354, 0.06137, 0.06256, 
                     0.07735, 0.062419, 0.06141, 0.06364, 0.062943, 
                     0.062407, 0.061387, 0.061401, 0.062413, 0.062522, 
                     0.062891, 0.046867, 0.061049, 0.061399, 0.061341, 
                     0.061378, 0.061402, 0.077008, 0.061409, 0.076644, 
                     0.062524, 0.062417, 0.062791, 0.093677, 0.061363, 
                     0.061391, 0.061357, 0.061398, 0.060927, 0.061397]
"""
list_fc_111_min = [0.061337, 0.062442, 0.077007, 0.06244, 0.076932, 
                    0.062398, 0.06242, 0.076928, 0.061069, 0.061383,
                     0.078007, 0.08021, 0.061399, 0.06114, 0.063035, 
                     0.092573, 0.092626, 0.09381, 0.077658, 0.062498, 
                     0.078124, 0.061565, 0.065407, 0.062364, 0.076982, 
                     0.061401, 0.07706, 0.062923, 0.060974, 0.062546, 
                     0.062497, 0.0614, 0.092279, 0.061408, 0.061418, 
                     0.078078, 0.077029, 0.077045, 0.076998, 0.062529, 
                     0.062408, 0.077009, 0.085933, 0.063623, 0.061574, 
                     0.077976, 0.078835, 0.07799, 0.060966, 0.13944, 
                     0.187647, 0.158812, 0.126163, 0.170783, 0.187475, 
                     0.092277, 0.109415, 0.127974, 0.171966, 0.170344, 
                     0.092636, 0.15622, 0.108305, 0.077035, 0.21837, 
                     0.108678, 0.108277, 0.0933, 0.09365, 0.108285, 
                     0.202039, 0.095694, 0.092581, 0.092656, 0.093787, 
                     0.109386, 0.110854, 0.126032, 0.093734, 0.108315, 
                     0.109452, 0.108179, 0.109798, 0.109276, 0.108236, 
                     0.094284, 0.108255, 0.155095, 0.10827, 0.108311, 
                     0.108261, 0.187412, 0.092612, 0.109245, 0.10931, 
                     0.124692, 0.186341, 0.093746, 0.108193, 0.108722, 
                     0.139534, 0.108243, 0.109008, 0.093699, 0.092318, 
                     0.156456, 0.108278, 0.140555, 0.219034, 0.108271, 
                     0.20305, 0.108236, 0.109424, 0.140648, 0.093667, 
                     0.140654, 0.139475, 0.109292, 0.092594, 0.092689, 
                     0.093565, 0.093581, 0.108287, 0.186429, 0.108297, 
                     0.092656, 0.186367, 0.109257, 0.092628, 0.109385, 
                     0.108189, 0.108182, 0.13954, 0.109396, 0.10822, 
                     0.078727, 0.092657, 0.094743, 0.108225, 0.158085, 
                     0.109283, 0.094532, 0.092657, 0.1265, 0.108287, 
                     0.108269, 0.110107, 0.108277, 0.092649, 0.108227, 
                     0.109284, 0.171918, 0.109413, 0.094474, 0.109234, 
                     0.094284, 0.155073, 0.094145, 0.079228, 0.156199, 
                     0.077052, 0.078091, 0.061381, 0.155268, 0.062924, 
                     0.078844, 0.062501, 0.061354, 0.06137, 0.06256, 
                     0.07735, 0.062419, 0.06141, 0.06364, 0.062943, 
                     0.062407, 0.061387, 0.061401, 0.062413, 0.062522, 
                     0.062891, 0.066867, 0.061049, 0.061399, 0.061341, 
                     0.061378, 0.061402, 0.077008, 0.061409, 0.076644, 
                     0.062524, 0.062417, 0.062791, 0.093677, 0.061363, 
                     0.061391, 0.061357, 0.061398, 0.060927, 0.061397]

#print(len(list_fc_111_min))

if False:
    plt.plot(list(range(len(list_fc_111_min))), list_fc_111_min, 'b-o')
    plt.xlim(0, 200)
    plt.ylim(0.0, 0.4)
    plt.title('FC: From REQUEST to RESPONSE')
    plt.show()

"""
3 : 2021-08-24-18-45-50-740861-DC-111.log
4 : 2021-08-24-18-51-22-552456-DC-111.log
5 : 2021-08-24-18-55-41-988560-DC-111.log
<min 값을 취한 결과>
list_dc_111_min = [0.068361, 0.064103, 0.061369, 0.048567, 0.062405, 
                    0.077025, 0.061984, 0.060968, 0.061419, 0.06136, 
                    0.062724, 0.062182, 0.062375, 0.062486, 0.061425, 
                    0.092298, 0.077042, 0.062826, 0.061673, 0.077595, 
                    0.077043, 0.061383, 0.06107, 0.076996, 0.078161, 
                    0.076989, 0.061392, 0.076985, 0.061429, 0.062301, 
                    0.061362, 0.069855, 0.092605, 0.092525, 0.076975, 
                    0.061389, 0.061383, 0.078073, 0.092637, 0.077025, 
                    0.062429, 0.078049, 0.061417, 0.061314, 0.07812, 
                    0.062954, 0.06136, 0.062501, 0.078107, 0.123865, 
                    0.093648, 0.108312, 0.093372, 0.233184, 0.131902, 
                    0.092671, 0.125449, 0.108288, 0.108279, 0.094192, 
                    0.092623, 0.140542, 0.093698, 0.061419, 0.061038, 
                    0.062487, 0.061366, 0.061175, 0.061399, 0.062432, 
                    0.061348, 0.076986, 0.077046, 0.062419, 0.07703, 
                    0.060974, 0.076997, 0.076981, 0.062413, 0.062514, 
                    0.062523, 0.062513, 0.06249, 0.062357, 0.06138, 
                    0.062428, 0.076991, 0.061734, 0.061415, 0.076588, 
                    0.061349, 0.078883, 0.076824, 0.063628, 0.078049, 
                    0.063287, 0.061399, 0.061408, 0.065753, 0.06505, 
                    0.060664, 0.066787, 0.155169, 0.062442, 0.070323, 
                    0.062414, 0.062473, 0.061419, 0.061389, 0.061391, 
                    0.09266, 0.061936, 0.061984, 0.061427, 0.061044, 
                    0.061072, 0.06136, 0.061371, 0.061402, 0.064187, 
                    0.049246, 0.062511, 0.062421, 0.063892, 0.062354, 
                    0.062496, 0.066397, 0.0614, 0.063359, 0.06098, 
                    0.0624, 0.061371, 0.063854, 0.050368, 0.062489, 
                    0.061356, 0.061339, 0.061377, 0.06241, 0.062517, 
                    0.058446, 0.062939, 0.06459, 0.061378, 0.062545, 
                    0.049873, 0.063121, 0.064669, 0.063194, 0.061345, 
                    0.092219, 0.061312, 0.065169, 0.066378, 0.061401, 
                    0.045774, 0.07701, 0.067351, 0.076641, 0.047511, 
                    0.07707, 0.079593, 0.061356, 0.065182, 0.055917, 
                    0.077015, 0.061097, 0.062206, 0.062657, 0.064243, 
                    0.060964, 0.078063, 0.099397, 0.061372, 0.061363, 
                    0.062411, 0.066299, 0.066793, 0.062369, 0.062444, 
                    0.061387, 0.062803, 0.062543, 0.063047, 0.064135, 
                    0.062991, 0.047358, 0.064074, 0.047803, 0.061423, 
                    0.061376, 0.06266, 0.063445, 0.064275, 0.062389, 
                    0.061408, 0.06654, 0.062377, 0.061382, 0.073383]
"""
list_dc_111_min = [0.068361, 0.064103, 0.061369, 0.068567, 0.062405, 
                    0.077025, 0.061984, 0.060968, 0.061419, 0.06136, 
                    0.062724, 0.062182, 0.062375, 0.062486, 0.061425, 
                    0.092298, 0.077042, 0.062826, 0.061673, 0.077595, 
                    0.077043, 0.061383, 0.06107, 0.076996, 0.078161, 
                    0.076989, 0.061392, 0.076985, 0.061429, 0.062301, 
                    0.061362, 0.069855, 0.092605, 0.092525, 0.076975, 
                    0.061389, 0.061383, 0.078073, 0.092637, 0.077025, 
                    0.062429, 0.078049, 0.061417, 0.061314, 0.07812, 
                    0.062954, 0.061360, 0.062501, 0.078107, 0.123865, 
                    0.093648, 0.108312, 0.093372, 0.133184, 0.131902, 
                    0.092671, 0.125449, 0.108288, 0.108279, 0.094192, 
                    0.092623, 0.140542, 0.093698, 0.061419, 0.061038, 
                    0.062487, 0.061366, 0.061175, 0.061399, 0.062432, 
                    0.061348, 0.076986, 0.077046, 0.062419, 0.07703, 
                    0.060974, 0.076997, 0.076981, 0.062413, 0.062514, 
                    0.062523, 0.062513, 0.062490, 0.062357, 0.06138, 
                    0.062428, 0.076991, 0.061734, 0.061415, 0.076588, 
                    0.061349, 0.078883, 0.076824, 0.063628, 0.078049, 
                    0.063287, 0.061399, 0.061408, 0.065753, 0.06505, 
                    0.060664, 0.066787, 0.095169, 0.062442, 0.070323, 
                    0.062414, 0.062473, 0.061419, 0.061389, 0.061391, 
                    0.092660, 0.061936, 0.061984, 0.061427, 0.061044, 
                    0.061072, 0.061360, 0.061371, 0.061402, 0.064187, 
                    0.069246, 0.062511, 0.062421, 0.063892, 0.062354, 
                    0.062496, 0.066397, 0.061400, 0.063359, 0.06098, 
                    0.062400, 0.061371, 0.063854, 0.060368, 0.062489, 
                    0.061356, 0.061339, 0.061377, 0.062410, 0.062517, 
                    0.058446, 0.062939, 0.064590, 0.061378, 0.062545, 
                    0.069873, 0.063121, 0.064669, 0.063194, 0.061345, 
                    0.092219, 0.061312, 0.065169, 0.066378, 0.061401, 
                    0.065774, 0.077010, 0.067351, 0.076641, 0.067511, 
                    0.077070, 0.079593, 0.061356, 0.065182, 0.055917, 
                    0.077015, 0.061097, 0.062206, 0.062657, 0.064243, 
                    0.060964, 0.078063, 0.099397, 0.061372, 0.061363, 
                    0.062411, 0.066299, 0.066793, 0.062369, 0.062444, 
                    0.061387, 0.062803, 0.062543, 0.063047, 0.064135, 
                    0.062991, 0.067358, 0.064074, 0.067803, 0.061423, 
                    0.061376, 0.062660, 0.063445, 0.064275, 0.062389, 
                    0.061408, 0.066540, 0.062377, 0.061382, 0.073383]

#print(len(list_fc_111_min))

if False:
    plt.plot(list(range(len(list_dc_111_min))), list_dc_111_min, 'b-o')
    plt.xlim(0, 200)
    plt.ylim(0.0, 0.4)
    plt.title('DC: From REQUEST to RESPONSE')
    plt.show()

"""
6 : 2021-08-24-19-02-46-641987-LR-111.log
7 : 2021-08-24-19-07-06-199555-LR-111.log
8 : 2021-08-24-19-11-33-672913-LR-111.log
<min 값을 취한 결과>
list_lr_111_min = [0.06221, 0.076974, 0.061365, 0.060951, 0.062401, 
                0.062726, 0.061392, 0.063776, 0.061406, 0.061386, 
                0.063015, 0.06139, 0.079088, 0.06141, 0.070429, 
                0.092291, 0.077986, 0.061382, 0.092696, 0.078046, 
                0.062535, 0.06224, 0.076997, 0.061402, 0.063185, 
                0.076586, 0.078075, 0.062506, 0.078034, 0.092666, 
                0.06252, 0.062197, 0.077008, 0.092924, 0.076958, 
                0.062522, 0.061362, 0.093737, 0.062497, 0.061061, 
                0.07707, 0.063456, 0.086039, 0.061404, 0.062421, 
                0.061478, 0.078052, 0.092666, 0.061395, 0.064485, 
                0.173223, 0.166085, 0.13948, 0.108301, 0.092616, 
                0.062419, 0.061395, 0.078057, 0.07702, 0.061396, 
                0.078348, 0.062114, 0.063545, 0.077006, 0.061407, 
                0.204000, 0.06097, 0.061339, 0.062936, 0.061308, 
                0.061362, 0.061414, 0.061409, 0.062407, 0.061376, 
                0.06139, 0.062495, 0.0614, 0.061408, 0.078035, 
                0.078052, 0.060963, 0.061393, 0.064055, 0.061023, 
                0.061574, 0.062347, 0.063013, 0.062533, 0.062551, 
                0.061401, 0.076973, 0.061351, 0.06192, 0.061398, 
                0.061361, 0.063306, 0.061357, 0.062412, 0.078099, 
                0.061478, 0.06209, 0.062576, 0.061067, 0.062503, 
                0.062981, 0.062359, 0.061398, 0.061092, 0.062508, 
                0.062367, 0.047173, 0.07684, 0.155098, 0.070471, 
                0.061416, 0.079034, 0.061351, 0.077009, 0.062469, 
                0.061442, 0.061385, 0.061358, 0.061358, 0.061032, 
                0.061334, 0.062572, 0.061397, 0.062435, 0.078549, 
                0.063109, 0.061407, 0.061386, 0.061381, 0.061377, 
                0.062384, 0.061403, 0.062097, 0.062419, 0.061061, 
                0.061417, 0.062981, 0.061339, 0.062426, 0.062394, 
                0.077046, 0.062506, 0.06244, 0.061324, 0.061221, 
                0.061415, 0.061367, 0.061363, 0.061389, 0.060974, 
                0.06136, 0.061415, 0.077006, 0.061411, 0.061383, 
                0.063557, 0.07699, 0.061358, 0.062411, 0.061007, 
                0.066284, 0.061397, 0.062499, 0.061215, 0.061345, 
                0.061392, 0.061455, 0.046598, 0.061375, 0.061358, 
                0.061381, 0.061201, 0.062008, 0.062356, 0.061398, 
                0.062877, 0.061393, 0.061408, 0.062584, 0.062504, 
                0.062476, 0.061358, 0.062469, 0.047416, 0.06139, 
                0.077044, 0.061051, 0.078038, 0.046785, 0.061415, 
                0.061399, 0.061372, 0.077045, 0.062518, 0.062086]
"""
list_lr_111_min = [0.06221, 0.076974, 0.061365, 0.060951, 0.062401, 
                0.062726, 0.061392, 0.063776, 0.061406, 0.061386, 
                0.063015, 0.061390, 0.079088, 0.06141, 0.070429, 
                0.092291, 0.077986, 0.061382, 0.092696, 0.078046, 
                0.062535, 0.062240, 0.076997, 0.061402, 0.063185, 
                0.076586, 0.078075, 0.062506, 0.078034, 0.092666, 
                0.062520, 0.062197, 0.077008, 0.092924, 0.076958, 
                0.062522, 0.061362, 0.093737, 0.062497, 0.061061, 
                0.077070, 0.063456, 0.086039, 0.061404, 0.062421, 
                0.061478, 0.078052, 0.092666, 0.061395, 0.064485, 
                0.173223, 0.139480, 0.166085, 0.108301, 0.092616, 
                0.104000, 0.061395, 0.078057, 0.077020, 0.061396, 
                0.078348, 0.062114, 0.063545, 0.077006, 0.061407, 
                0.062419, 0.060970, 0.061339, 0.062936, 0.061308, 
                0.061362, 0.061414, 0.061409, 0.062407, 0.061376, 
                0.061390, 0.062495, 0.061400, 0.061408, 0.078035, 
                0.078052, 0.060963, 0.061393, 0.064055, 0.061023, 
                0.061574, 0.062347, 0.063013, 0.062533, 0.062551, 
                0.061401, 0.076973, 0.061351, 0.061920, 0.061398, 
                0.061361, 0.063306, 0.061357, 0.062412, 0.078099, 
                0.061478, 0.062090, 0.062576, 0.061067, 0.062503, 
                0.062981, 0.062359, 0.061398, 0.061092, 0.062508, 
                0.062367, 0.067173, 0.076840, 0.105098, 0.070471, 
                0.061416, 0.079034, 0.061351, 0.077009, 0.062469, 
                0.061442, 0.061385, 0.061358, 0.061358, 0.061032, 
                0.061334, 0.062572, 0.061397, 0.062435, 0.078549, 
                0.063109, 0.061407, 0.061386, 0.061381, 0.061377, 
                0.062384, 0.061403, 0.062097, 0.062419, 0.061061, 
                0.061417, 0.062981, 0.061339, 0.062426, 0.062394, 
                0.077046, 0.062506, 0.062440, 0.061324, 0.061221, 
                0.061415, 0.061367, 0.061363, 0.061389, 0.060974, 
                0.061360, 0.061415, 0.077006, 0.061411, 0.061383, 
                0.063557, 0.076990, 0.061358, 0.062411, 0.061007, 
                0.066284, 0.061397, 0.062499, 0.061215, 0.061345, 
                0.061392, 0.061455, 0.066598, 0.061375, 0.061358, 
                0.061381, 0.061201, 0.062008, 0.062356, 0.061398, 
                0.062877, 0.061393, 0.061408, 0.062584, 0.062504, 
                0.062476, 0.061358, 0.062469, 0.067416, 0.061390, 
                0.077044, 0.061051, 0.078038, 0.066785, 0.061415, 
                0.061399, 0.061372, 0.077045, 0.062518, 0.062086]

#print(len(list_fc_111_min))

if False:
    plt.plot(list(range(len(list_lr_111_min))), list_lr_111_min, 'b-o')
    plt.xlim(0, 200)
    plt.ylim(0.0, 0.4)
    plt.title('LR: From REQUEST to RESPONSE')
    plt.show()

if True:
    # 하나의 그림으로 통합
    fc_avg = sum(list_fc_111_min) / len(list_fc_111_min)
    dc_avg = sum(list_dc_111_min) / len(list_dc_111_min)
    lr_avg = sum(list_lr_111_min) / len(list_lr_111_min)
    rg = list(range(len(list_lr_111_min)))
    plt.plot(rg, list_fc_111_min, 'b-')
    plt.plot(rg, list_dc_111_min, 'r-')
    plt.plot(rg, list_lr_111_min, 'k-')
    plt.legend(['FC','DC','LR'])
    plt.xlim(0, 200)
    plt.ylim(0.0, 0.5)
    plt.xlabel('Request ID')
    plt.ylabel('Delay (second)')
    #plt.title('RTT, avg is FC({}), DC({}), LR({})'.format(fc_avg,dc_avg,lr_avg))
    plt.show()
    print('RTT, avg is FC({}), DC({}), LR({})'.format(fc_avg,dc_avg,lr_avg))