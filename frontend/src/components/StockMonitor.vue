<template>
    <div class="container">
      <h3>竞价监控系统</h3>
      
      <div class="controls">
        <button @click="fetchData">手动刷新</button>
        <span>自动刷新间隔：15秒</span>
      </div>
  
      <div v-if="loading" class="loading">加载中...</div>
      
      <table v-else>
        <thead>
          <tr>
            <th>代码</th>
            <th>名称</th>
            <th>估分</th>
            <th>今日涨幅%</th>
            <th>昨日涨幅%</th>
            <th>现价</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="stock in stocks" :key="stock.code">
            <td>{{ codeFormat(stock.code) }}</td>
            <td>{{ stock.name }}</td>
            <td>{{ stock.score }}</td>
            <td :class="{ 'up': stock.change > 0, 'down': stock.change < 0 }">
              {{ formatChange(stock.change) }}
            </td>
            <td :class="{ 'up': stock.open_rise > 0, 'down': stock.open_rise < 0 }">
              {{ formatChange(stock.open_rise) }}
            </td>
            <td>{{ stock.price }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, onUnmounted } from 'vue';
  import axios from 'axios';
  
  const stocks = ref([]);
  const loading = ref(false);
  let autoRefreshTimer = null;
  
  const fetchData = async () => {
    loading.value = true;
    try {
      const response = await axios.get('http://localhost:3838/api/stocks');
      console.log(response.data)
      stocks.value = processData(response.data.data);
    } catch (error) {
      console.error('数据获取失败:', error);
    } finally {
      loading.value = false;
    }
  };
  
  const processData = (rawData) => {
    console.log(rawData)
    return rawData.map(item => ({
      code: item.code,
      name: item.name,
      score: Math.round(item.score),
      change: parseFloat(item.change),
      price: parseFloat(item.price),
      open_rise: parseFloat(item.open_rise)
    }));
  };
  
  // 自动刷新逻辑
  onMounted(() => {
    fetchData(); // 首次加载
    autoRefreshTimer = setInterval(fetchData, 15000);
  });
  
  onUnmounted(() => {
    clearInterval(autoRefreshTimer);
  });
  
  const codeFormat = (code) => code.padStart(6, '0');
  const formatChange = (value) => 
    `${value > 0 ? '▲' : '▼'} ${Math.abs(value).toFixed(2)}%`;
  </script>
  
  <style scoped>
  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
  }
  
  .controls {
    margin: 20px 0;
    display: flex;
    gap: 10px;
    align-items: center;
  }
  
  .loading {
    text-align: center;
    color: #666;
  }
  
  table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
  }
  
  th, td {
    padding: 12px;
    border: 1px solid #eee;
    text-align: left;
  }
  
  th {
    background-color: #f8f9fa;
  }
  
  .up {
    color: #dc3545;
  }
  
  .down {
    color: #28a745;
  }
  </style>