clc
clear

%读取仿真结果
net_sinr = csvread('net_V2I_sinr.csv');
graph_sinr = csvread('graph_V2I_sinr.csv');

h1 = cdfplot(net_sinr);
set(h1,'color','r','linewidth',1)
hold on;
h2 = cdfplot(graph_sinr);
set(h2,'color','b','linewidth',1)

h=legend([h1,h2],'neural network','gragh coloring','Location','SouthEast');
set(h,'Fontsize',13);
xlabel('SINR(dB)');
ylabel('CDF');
grid on;
title('V2I SINR CDF')