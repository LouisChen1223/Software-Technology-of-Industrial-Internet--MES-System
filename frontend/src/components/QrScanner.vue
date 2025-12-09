<template>
  <div>
    <div style="margin-bottom:8px">
      <el-select v-model="deviceId" placeholder="选择摄像头" style="width:260px" @change="restart">
        <el-option v-for="d in devices" :key="d.deviceId" :label="d.label || d.deviceId" :value="d.deviceId"/>
      </el-select>
      <el-button size="small" @click="restart">重启</el-button>
    </div>
    <video ref="videoRef" style="width:100%;max-width:480px;border:1px solid #eee" autoplay muted playsinline></video>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { BrowserMultiFormatReader } from '@zxing/browser'

const emit = defineEmits<{ (e: 'detected', code: string): void }>()

const codeReader = new BrowserMultiFormatReader()
const videoRef = ref<HTMLVideoElement | null>(null)
const devices = ref<MediaDeviceInfo[]>([])
const deviceId = ref<string>('')
let stopFn: (() => void) | null = null

async function start() {
  if (!videoRef.value) return
  try {
    stop()
    const controls = await codeReader.decodeFromVideoDevice(deviceId.value || undefined, videoRef.value, (result) => {
      if (result) {
        emit('detected', result.getText())
        stop()
      }
    })
    stopFn = () => controls.stop()
  } catch (e) {
    console.error(e)
  }
}

function stop() { if (stopFn) { stopFn(); stopFn = null } }
function restart() { start() }

onMounted(async () => {
  try {
    const list = await BrowserMultiFormatReader.listVideoInputDevices()
    devices.value = list
    deviceId.value = (list[0] && list[0].deviceId) || ''
  } finally {
    start()
  }
})

onBeforeUnmount(stop)
</script>
