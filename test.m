clc
clear

%网络加载
load('-mat','trained_net'); 

%读取测试数据
testData = csvread('testData.csv');
test_highway = testData(:, 1);
test_suburban = testData(:, 2);
test_urban = testData(:, 3);
test_t_reverse = testData(:, 4);
test_t_forward = testData(:, 5);
test_t_convoy = testData(:, 6);
test_i_reverse = testData(:, 7);
test_i_forward = testData(:, 8);
test_i_convoy = testData(:, 9);
test_target_distance = testData(:,10);
test_inter_distance = testData(:, 11);
test_target_power = testData(:, 12);
test_inter_power	= testData(:, 13);
test_weight = testData(:, 14);
test_inter_class = testData(:, 15);

test_tx_id = testData(:, 16);
test_rx_id = testData(:, 17);
test_id = testData(:, 18);

class_result = [test_id, test_tx_id, test_rx_id];

%归一化
[testInput,~] = mapminmax([test_highway, test_suburban, test_urban, test_t_reverse, test_t_forward, test_t_convoy,...
    test_i_reverse, test_i_forward, test_i_convoy, test_target_distance, test_inter_distance, test_target_power, test_inter_power]');

%放入到网络输出数据
testOuput = sim(net, testInput);

%统计识别正确率
[s1 , s2] = size(testOuput);
hitNum = 0 ;
for i = 1 : s2
    [m , Index] = max(testOuput(:, i)); 
    class_result(i, 4) = Index;
    if(Index  == test_inter_class(i)) 
        hitNum = hitNum + 1 ; 
    end
end

 csvwrite('class.csv', class_result)

sprintf('rate: %3.3f%%', 100 * hitNum / s2 )