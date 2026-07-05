<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="modelValue" class="bw-modal__mask" @click="handleMaskClick">
        <Transition name="modal-slide">
          <div v-if="modelValue" class="bw-modal__wrapper" @click.stop>
            <div :class="['bw-modal', `bw-modal--${size}`]">
              <!-- 头部 -->
              <div v-if="$slots.header || title" class="bw-modal__header">
                <slot name="header">
                  <h3 class="bw-modal__title">{{ title }}</h3>
                </slot>
                <button 
                  v-if="closable"
                  class="bw-modal__close"
                  @click="handleClose"
                >
                  ✕
                </button>
              </div>
              
              <!-- 内容 -->
              <div class="bw-modal__body">
                <slot></slot>
              </div>
              
              <!-- 底部 -->
              <div v-if="$slots.footer || showFooter" class="bw-modal__footer">
                <slot name="footer">
                  <BWButton @click="handleClose">取消</BWButton>
                  <BWButton type="primary" :loading="loading" @click="handleConfirm">
                    确定
                  </BWButton>
                </slot>
              </div>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import BWButton from './BWButton.vue'

defineProps({
  modelValue: Boolean,
  title: String,
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  closable: {
    type: Boolean,
    default: true
  },
  maskClosable: {
    type: Boolean,
    default: true
  },
  showFooter: {
    type: Boolean,
    default: true
  },
  loading: Boolean
})

const emit = defineEmits(['update:modelValue', 'confirm', 'close'])

const handleClose = () => {
  emit('update:modelValue', false)
  emit('close')
}

const handleConfirm = () => {
  emit('confirm')
}

const handleMaskClick = () => {
  if (props.maskClosable) {
    handleClose()
  }
}
</script>

<style scoped>
.bw-modal__mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.bw-modal__wrapper {
  max-width: 100%;
  max-height: 100%;
  overflow: auto;
}

.bw-modal {
  background: var(--bg-elevated);
  border: 1px solid var(--border-primary);
  border-radius: 12px;
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - 40px);
}

.bw-modal--small {
  width: 400px;
}

.bw-modal--medium {
  width: 600px;
}

.bw-modal--large {
  width: 800px;
}

.bw-modal__header {
  position: relative;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-secondary);
}

.bw-modal__title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  padding-right: 30px;
}

.bw-modal__close {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  color: var(--text-tertiary);
  font-size: 18px;
  cursor: pointer;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}

.bw-modal__close:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.bw-modal__body {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.6;
}

.bw-modal__footer {
  padding: 16px 24px;
  border-top: 1px solid var(--border-secondary);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 动画 */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity var(--transition-normal);
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-slide-enter-active,
.modal-slide-leave-active {
  transition: all var(--transition-normal);
}

.modal-slide-enter-from {
  opacity: 0;
  transform: translateY(-30px);
}

.modal-slide-leave-to {
  opacity: 0;
  transform: translateY(30px);
}

/* 响应式 */
@media (max-width: 768px) {
  .bw-modal--small,
  .bw-modal--medium,
  .bw-modal--large {
    width: 100%;
    max-width: calc(100vw - 40px);
  }
  
  .bw-modal__header,
  .bw-modal__body,
  .bw-modal__footer {
    padding-left: 16px;
    padding-right: 16px;
  }
}
</style>
