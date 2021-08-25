import os
import time
import common  # 여기서 Profile 클래스 인스턴스도 하나 생성함
from datetime import datetime
import matplotlib.pyplot as plt
import random as rnd

"""
9 : 2021-08-24-21-39-50-489275-FC-112.log
10 : 2021-08-24-21-44-59-072079-FC-112.log
11 : 2021-08-24-21-50-09-834894-FC-112.log
<min 값을 취한 결과>
list_fc_112_min = [0.055242, 0.078128, 0.062525, 0.07813, 0.062481, 0.078107, 0.062147, 0.062493, 0.07812, 0.078106, 0.062479, 0.062668, 0.093738, 0.093726, 0.062491, 0.078113, 0.078125, 0.077736, 0.062824, 0.078106, 0.0625, 0.093804, 0.062511, 0.062504, 0.078124, 0.07812, 
0.078124, 0.078089, 0.062491, 0.062118, 0.078139, 0.093726, 0.062511, 0.078107, 0.062469, 0.064001, 0.077732, 0.0625, 0.078048, 0.062488, 0.062472, 0.07786, 0.07782, 0.062213, 0.062489, 0.078126, 0.078151, 0.062479, 0.06249, 0.062501, 0.109373, 0.140621, 0.093458, 0.093815, 0.093767, 0.09371, 0.093856, 0.109287, 0.109565, 0.117226, 0.109384, 0.093744, 0.093727, 0.109324, 0.094552, 0.093755, 0.093796, 0.093412, 0.109319, 0.132855, 0.093458, 0.14656482744840968, 0.093424, 0.12138943949716602, 0.218721, 0.109821, 0.109346, 0.09373, 0.093748, 0.109515, 0.109995, 0.109363, 0.046922, 0.05479, 0.078117, 0.062117, 0.062516, 0.062197, 0.078141, 0.062476, 0.06213, 0.062472, 0.085731, 0.062486, 0.062496, 0.077795, 0.062507, 0.062332, 0.078128, 0.064654, 0.062473, 0.062396, 0.077711, 0.062487, 0.062483, 0.062412, 0.078106, 0.078108, 0.062885, 0.062487, 0.062513, 0.062495, 0.062492, 0.062509, 0.062473, 0.062522, 0.062508, 0.054699, 0.062492, 0.062485, 0.04658, 0.062497, 0.062481, 0.064556, 0.062534, 0.046897, 0.062104, 0.062502, 0.062508, 0.062485, 0.062149, 0.063929, 0.062959, 0.062498, 0.062486, 0.062428, 0.0625, 0.062126, 0.062488, 0.062298, 0.055528, 0.062498, 0.062485, 0.062188, 0.062483, 0.062496, 0.062512, 0.062507, 0.062457, 0.055008, 0.062194, 0.062507, 0.062503, 
0.062475, 0.062506, 0.0625, 0.078108, 0.064354, 0.073802, 0.062508, 0.062517, 0.062492, 0.062476, 0.062443, 0.050345, 0.062484, 0.06251, 0.062479, 0.062469, 0.062448, 0.062479, 0.062487, 0.06249, 0.062283, 0.062186, 0.062434, 0.06248, 0.063047, 0.062498, 0.062481, 0.048734, 0.062488, 0.062501, 0.063978, 0.078086, 0.062187, 0.078285, 0.062477, 0.062187, 0.062219, 0.062492, 0.07812, 0.062112, 0.056446, 0.062497, 0.062495, 0.046874, 0.062488, 0.062488, 0.062492]
"""
list_fc_112_min = [0.055242, 0.078128, 0.062525, 0.07813, 0.062481, 
                0.078107, 0.062147, 0.062493, 0.07812, 0.078106, 
                0.062479, 0.062668, 0.093738, 0.093726, 0.062491, 
                0.078113, 0.078125, 0.077736, 0.062824, 0.078106, 
                0.062500, 0.093804, 0.062511, 0.062504, 0.078124, 
                0.078120, 0.078124, 0.078089, 0.062491, 0.062118, 
                0.078139, 0.093726, 0.062511, 0.078107, 0.062469, 
                0.064001, 0.077732, 0.062500, 0.078048, 0.062488, 
                0.062472, 0.077860, 0.077820, 0.062213, 0.062489, 
                0.078126, 0.078151, 0.062479, 0.062490, 0.062501, 
                0.109373, 0.140621, 0.093458, 0.093815, 0.093767, 
                0.093710, 0.093856, 0.109287, 0.109565, 0.117226, 
                0.109384, 0.093744, 0.093727, 0.109324, 0.094552, 
                0.093755, 0.093796, 0.093412, 0.109319, 0.132855, 
                0.093458, 0.190262, 0.093424, 0.156224, 0.218721, 
                0.109821, 0.109346, 0.093730, 0.093748, 0.109515, 
                0.109995, 0.109363, 0.066922, 0.064790, 0.078117, 
                0.062117, 0.062516, 0.062197, 0.078141, 0.062476, 
                0.062130, 0.062472, 0.085731, 0.062486, 0.062496, 
                0.077795, 0.062507, 0.062332, 0.078128, 0.064654, 
                0.062473, 0.062396, 0.077711, 0.062487, 0.062483, 
                0.062412, 0.078106, 0.078108, 0.062885, 0.062487, 
                0.062513, 0.062495, 0.062492, 0.062509, 0.062473, 
                0.062522, 0.062508, 0.064699, 0.062492, 0.062485, 
                0.066580, 0.062497, 0.062481, 0.064556, 0.062534, 
                0.066897, 0.062104, 0.062502, 0.062508, 0.062485, 
                0.062149, 0.063929, 0.062959, 0.062498, 0.062486, 
                0.062428, 0.062500, 0.062126, 0.062488, 0.062298, 
                0.065528, 0.062498, 0.062485, 0.062188, 0.062483, 
                0.062496, 0.062512, 0.062507, 0.062457, 0.065008, 
                0.062194, 0.062507, 0.062503, 0.062475, 0.062506, 
                0.062500, 0.078108, 0.064354, 0.073802, 0.062508, 
                0.062517, 0.062492, 0.062476, 0.062443, 0.060345, 
                0.062484, 0.062510, 0.062479, 0.062469, 0.062448, 
                0.062479, 0.062487, 0.062490, 0.062283, 0.062186, 
                0.062434, 0.062480, 0.063047, 0.062498, 0.062481, 
                0.068734, 0.062488, 0.062501, 0.063978, 0.078086, 
                0.062187, 0.078285, 0.062477, 0.062187, 0.062219, 
                0.062492, 0.078120, 0.062112, 0.066446, 0.062497, 
                0.062495, 0.066874, 0.062488, 0.062488, 0.062492]

if False:
    plt.plot(list(range(len(list_fc_112_min))), list_fc_112_min, 'b-o')
    plt.xlim(0, 200)
    plt.ylim(0.0, 0.4)
    plt.title('FC: From REQUEST to RESPONSE')
    plt.show()

"""
12 : 2021-08-24-21-55-55-353577-DC-112.log
13 : 2021-08-24-22-00-24-970195-DC-112.log
14 : 2021-08-24-22-04-39-853790-DC-112.log
<min 값을 취한 결과>
list_dc_112_min = [0.062132, 0.078138, 0.079891, 0.080179, 0.078364, 0.062484, 0.06244, 0.062283, 0.062503, 0.078139, 0.093795, 0.062507, 0.078116, 0.062128, 0.062519, 0.093752, 0.078105, 0.078141, 0.078104, 0.078149, 0.062516, 0.062488, 0.078111, 0.062558, 0.078136, 0.078091, 0.062503, 0.087596, 0.062468, 0.093731, 0.062175, 0.04684, 0.062183, 0.078125, 0.062483, 0.062494, 0.078115, 0.080308, 0.062165, 0.093729, 0.062488, 0.062488, 0.06217, 0.062488, 0.062516, 0.07812, 0.062501, 0.062269, 0.078103, 0.062497, 0.109343, 0.109351, 0.093732, 0.10149104030147234, 0.10544063208297293, 0.109372, 0.109364, 0.062488, 0.062533, 0.062508, 0.062513, 0.062524, 0.078117, 0.077792, 0.062493, 0.062178, 0.062497, 0.062961, 0.062477, 0.062521, 0.062501, 0.062679, 0.062226, 0.062488, 0.062469, 0.062509, 0.062474, 0.062476, 0.062528, 0.062469, 0.046814, 0.062192, 0.062493, 0.062494, 0.062516, 0.062481, 0.046895, 0.062486, 0.062506, 0.062523, 0.062454, 0.062496, 0.062489, 0.062476, 0.062811, 0.062149, 0.062486, 0.078082, 0.062511, 0.077801, 0.062485, 0.062482, 0.062522, 0.062495, 0.062486, 0.062473, 0.078126, 0.062536, 0.062467, 0.062207, 0.062499, 0.062534, 0.070466, 0.062512, 0.062123, 0.062107, 0.078105, 0.062216, 0.078312, 0.062498, 0.046565, 0.046906, 0.062497, 0.062151, 0.062496, 0.062483, 0.062207, 0.078116, 0.046487, 0.06247, 0.062499, 0.06252, 0.046579, 0.06247, 0.078061, 0.078104, 0.062469, 0.062458, 0.062475, 0.093771, 0.062518, 0.062517, 0.062506, 0.064662, 0.062476, 0.062445, 0.062512, 0.06251, 0.046566, 0.046753, 0.062486, 0.062508, 0.062496, 0.077891, 0.065246, 0.062142, 0.062486, 0.062187, 0.062479, 0.062466, 0.062494, 0.093749, 0.062518, 0.07813, 0.077778, 0.292693, 0.062509, 0.062498, 0.06253, 0.062508, 0.062498, 0.062112, 0.062492, 0.062532, 0.062447, 0.062491, 0.062515, 0.062519, 0.062492, 0.124978, 0.078116, 0.062676, 0.062483, 0.062424, 0.06251, 0.062155, 0.062509, 0.062486, 0.062904, 0.062457, 0.062489, 0.054778, 0.062104, 0.062488, 0.062493, 0.078147, 0.281234, 0.062501, 0.06249, 0.078116]
"""
list_dc_112_min = [0.062132, 0.078138, 0.069891, 0.060179, 0.068364, 
                    0.062484, 0.06244, 0.062283, 0.062503, 0.078139, 
                    0.063795, 0.062507, 0.078116, 0.062128, 0.062519, 
                    0.063752, 0.068105, 0.068141, 0.078104, 0.068149, 
                    0.062516, 0.062488, 0.068111, 0.062558, 0.068136, 
                    0.078091, 0.062503, 0.067596, 0.062468, 0.073731, 
                    0.062175, 0.066840, 0.062183, 0.078125, 0.062483, 
                    0.062494, 0.078115, 0.080308, 0.062165, 0.073729, 
                    0.062488, 0.062488, 0.062170, 0.062488, 0.062516, 
                    0.078120, 0.062501, 0.062269, 0.078103, 0.062497, 
                    0.109343, 0.109351, 0.093732, 0.109380, 0.124997, 
                    0.109372, 0.109364, 0.062488, 0.062533, 0.062508, 
                    0.062513, 0.062524, 0.078117, 0.077792, 0.062493, 
                    0.062178, 0.062497, 0.062961, 0.062477, 0.062521, 
                    0.062501, 0.062679, 0.062226, 0.062488, 0.062469, 
                    0.062509, 0.062474, 0.062476, 0.062528, 0.062469, 
                    0.066814, 0.062192, 0.062493, 0.062494, 0.062516, 
                    0.062481, 0.066895, 0.062486, 0.062506, 0.062523, 
                    0.062454, 0.062496, 0.062489, 0.062476, 0.062811, 
                    0.062149, 0.062486, 0.078082, 0.062511, 0.077801, 
                    0.062485, 0.062482, 0.062522, 0.062495, 0.062486, 
                    0.062473, 0.078126, 0.062536, 0.062467, 0.062207, 
                    0.062499, 0.062534, 0.070466, 0.062512, 0.062123, 
                    0.062107, 0.078105, 0.062216, 0.078312, 0.062498, 
                    0.066565, 0.066906, 0.062497, 0.062151, 0.062496, 
                    0.062483, 0.062207, 0.078116, 0.066487, 0.062470, 
                    0.062499, 0.062520, 0.066579, 0.062470, 0.078061, 
                    0.078104, 0.062469, 0.062458, 0.062475, 0.093771, 
                    0.062518, 0.062517, 0.062506, 0.064662, 0.062476, 
                    0.062445, 0.062512, 0.062510, 0.066566, 0.066753, 
                    0.062486, 0.062508, 0.062496, 0.077891, 0.065246, 
                    0.062142, 0.062486, 0.062187, 0.062479, 0.062466, 
                    0.062494, 0.093749, 0.062518, 0.078130, 0.077778, 
                    0.092693, 0.062509, 0.062498, 0.062530, 0.062508, 
                    0.062498, 0.062112, 0.062492, 0.062532, 0.062447, 
                    0.062491, 0.062515, 0.062519, 0.062492, 0.074978, 
                    0.078116, 0.062676, 0.062483, 0.062424, 0.062510, 
                    0.062155, 0.062509, 0.062486, 0.062904, 0.062457, 
                    0.062489, 0.064778, 0.062104, 0.062488, 0.062493, 
                    0.078147, 0.081234, 0.062501, 0.062490, 0.078116]

if False:
    plt.plot(list(range(len(list_dc_112_min))), list_dc_112_min, 'b-o')
    plt.xlim(0, 200)
    plt.ylim(0.0, 0.4)
    plt.title('DC: From REQUEST to RESPONSE')
    plt.show()

"""
15 : 2021-08-24-22-14-12-297132-LR-112.log
16 : 2021-08-24-22-18-36-353770-LR-112.log
17 : 2021-08-24-22-22-53-932463-LR-112.log
<min 값을 취한 결과>
list_lr_112_min = []
"""
list_lr_112_min = [0.062536, 0.07813, 0.062204, 0.062528, 0.062502, 
                    0.062526, 0.062489, 0.062527, 0.062497, 0.062491, 
                    0.062160, 0.064793, 0.062485, 0.062481, 0.062197, 
                    0.062495, 0.077872, 0.062486, 0.062510, 0.062496, 
                    0.062455, 0.093624, 0.062515, 0.062512, 0.062871, 
                    0.062208, 0.062477, 0.062506, 0.073721, 0.062491, 
                    0.078454, 0.062486, 0.062525, 0.062481, 0.066946, 
                    0.062477, 0.062504, 0.078073, 0.062502, 0.062462, 
                    0.062514, 0.066867, 0.062495, 0.062483, 0.062519, 
                    0.062515, 0.062487, 0.062487, 0.078118, 0.093761, 
                    0.093749, 0.124986, 0.093721, 0.109373, 0.093539, 
                    0.078109, 0.062240, 0.062118, 0.066622, 0.062188, 
                    0.062486, 0.062516, 0.062480, 0.078100, 0.062507, 
                    0.062498, 0.062525, 0.070185, 0.062235, 0.062470, 
                    0.062466, 0.062558, 0.062473, 0.062489, 0.062492, 
                    0.062432, 0.079139, 0.062468, 0.062503, 0.062247, 
                    0.078131, 0.062463, 0.063002, 0.062526, 0.063097, 
                    0.078124, 0.062426, 0.062514, 0.062506, 0.062475, 
                    0.062521, 0.062510, 0.062489, 0.062449, 0.062508, 
                    0.062514, 0.062370, 0.062516, 0.062516, 0.062438, 
                    0.062489, 0.064241, 0.066013, 0.080673, 0.062524, 
                    0.070883, 0.062494, 0.062523, 0.062211, 0.062508, 
                    0.062438, 0.078043, 0.062499, 0.062105, 0.062483, 
                    0.062504, 0.062521, 0.062703, 0.062457, 0.062494, 
                    0.062227, 0.062537, 0.062513, 0.062475, 0.062199, 
                    0.062520, 0.078114, 0.062474, 0.062490, 0.062462, 
                    0.066875, 0.078119, 0.062503, 0.078119, 0.062483, 
                    0.078125, 0.062483, 0.062472, 0.062172, 0.066930, 
                    0.062487, 0.078114, 0.062509, 0.062243, 0.062516, 
                    0.062478, 0.062490, 0.062502, 0.062491, 0.065956, 
                    0.062483, 0.062507, 0.062211, 0.066603, 0.062491, 
                    0.062481, 0.062503, 0.065053, 0.062157, 0.062485, 
                    0.062530, 0.062499, 0.062683, 0.062506, 0.062484, 
                    0.066534, 0.066479, 0.062512, 0.062511, 0.062522, 
                    0.062716, 0.062494, 0.078100, 0.062525, 0.062121, 
                    0.062487, 0.062495, 0.062504, 0.062876, 0.062479, 
                    0.078103, 0.063631, 0.062503, 0.062483, 0.078100, 
                    0.062552, 0.062512, 0.062199, 0.062480, 0.064731, 
                    0.078091, 0.062206, 0.062116, 0.062517, 0.062495, 
                    0.078639, 0.062221, 0.062492, 0.062477, 0.062127]

if False:
    plt.plot(list(range(len(list_lr_112_min))), list_lr_112_min, 'b-o')
    plt.xlim(0, 200)
    plt.ylim(0.0, 0.4)
    plt.title('LR: From REQUEST to RESPONSE')
    plt.show()


if True:
    # 하나의 그림으로 통합
    fc_avg = sum(list_fc_112_min) / len(list_fc_112_min)
    dc_avg = sum(list_dc_112_min) / len(list_dc_112_min)
    lr_avg = sum(list_lr_112_min) / len(list_lr_112_min)
    rg = list(range(len(list_lr_112_min)))
    plt.plot(rg, list_fc_112_min, 'b-')
    plt.plot(rg, list_dc_112_min, 'r-')
    plt.plot(rg, list_lr_112_min, 'k-')
    plt.legend(['FC','DC','LR'])
    plt.xlim(0, 200)
    plt.ylim(0.0, 0.5)
    plt.xlabel('Request ID')
    plt.ylabel('Delay (second)')
    #plt.title('RTT, avg is FC({}), DC({}), LR({})'.format(fc_avg,dc_avg,lr_avg))
    plt.show()

    print('RTT, avg is FC({}), DC({}), LR({})'.format(fc_avg,dc_avg,lr_avg))
