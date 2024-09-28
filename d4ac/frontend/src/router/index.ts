import Vue from 'vue'
import VueRouter, { RouteConfig } from 'vue-router'
import DialogMainGoogle from '../views/DialogMainGoogle.vue'
import DialogMainAmazon from '../views/DialogMainAmazon.vue'
import DialogMainText from '../views/DialogMainText.vue'

Vue.use(VueRouter)

const routes: Array<RouteConfig> = [
  {
    path: '/',
    name: 'DialogMainGoogle',
    component: DialogMainGoogle
  },
  {
    path: '/Amazon',
    name: 'DialogMainAmazon',
    component: DialogMainAmazon
  },
  {
    path: '/Text',
    name: 'DialogMainText',
    component: DialogMainText
  }
]

const router = new VueRouter({
  mode: 'hash',
  base: process.env.BASE_URL,
  routes
})

export default router
