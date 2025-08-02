<!-- src/components/charts/DoughnutChart.vue -->
<template>
    <Doughnut :data="chartData" :options="chartOptions" />
  </template>
  
  <script setup>
  import { Doughnut } from 'vue-chartjs';
  import { Chart as ChartJS, Title, Tooltip, Legend, ArcElement, CategoryScale } from 'chart.js';
  
  ChartJS.register(Title, Tooltip, Legend, ArcElement, CategoryScale);
  
  defineProps({
    chartData: { type: Object, required: true },
    chartOptions: {
      type: Object,
      default: () => ({ responsive: true, maintainAspectRatio: false })
    }
  });
  </script>