<template>
  <div class="layout-container">
    <el-container>
      <el-aside width="220px" class="sidebar">
        <div class="logo">汽车销量数据平台</div>
        <el-menu :default-active="route.path" router background-color="#001529" text-color="#ffffffa6" active-text-color="#fff">
          <el-menu-item index="/">
            <el-icon><DataAnalysis /></el-icon>
            <span>仪表盘</span>
          </el-menu-item>
          <el-menu-item index="/market">
            <el-icon><TrendCharts /></el-icon>
            <span>整体市场</span>
          </el-menu-item>
          <el-menu-item index="/brands">
            <el-icon><Medal /></el-icon>
            <span>品牌排行</span>
          </el-menu-item>
          <el-menu-item index="/brands/compare">
            <el-icon><Switch /></el-icon>
            <span>品牌对比</span>
          </el-menu-item>
          <el-menu-item index="/analysis">
            <el-icon><PieChart /></el-icon>
            <span>数据分析</span>
          </el-menu-item>
          <el-menu-item index="/models">
            <el-icon><List /></el-icon>
            <span>车型排行</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-container>
        <el-header class="top-header">
          <TimeFilter />
        </el-header>
        <el-main class="main-content">
          <slot />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup lang="ts">
const route = useRoute();
</script>

<style scoped>
.layout-container {
  height: 100vh;
  overflow: hidden;
}
.sidebar {
  background: #001529;
  overflow-y: auto;
}
.logo {
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  padding: 20px 16px;
  text-align: center;
  border-bottom: 1px solid #ffffff1a;
}
.top-header {
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 0 24px;
  border-bottom: 1px solid #e8e8e8;
  height: 60px;
}
.main-content {
  background: #f0f2f5;
  min-height: calc(100vh - 60px);
  overflow-y: auto;
}
</style>