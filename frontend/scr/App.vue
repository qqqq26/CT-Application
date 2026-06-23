<!-- <script setup>
import HelloWorld from './components/HelloWorld.vue'
import TheWelcome from './components/TheWelcome.vue'
</script>

<template>
  <header>
    <img alt="Vue logo" class="logo" src="./assets/logo.svg" width="125" height="125" />

    <div class="wrapper">
      <HelloWorld msg="You did it!" />
    </div>
  </header>

  <main>
    <TheWelcome />
  </main>
</template>

<style scoped>
header {
  line-height: 1.5;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }
}
</style> -->
<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const logout = () => {
  localStorage.removeItem('user_token')
  router.push('/login')
}
</script>

<template>
  <div class="min-h-screen bg-gray-100 font-sans">
    <nav v-if="$route.name !== 'login'" class="bg-blue-900 text-white p-4 shadow-md flex justify-between items-center">
      <router-link to="/" class="text-3xl font-bold">CT Application</router-link>
      <button @click="logout" class="hover:underline">Logout</button>
    </nav>

    <main>
      <router-view />
    </main>
  </div>
</template>