<template>
  <div :class="['bw-input', { 'is-disabled': disabled }]">
    <label v-if="label" class="bw-input__label">
      {{ label }}
      <span v-if="required" class="bw-input__required">*</span>
    </label>
    
    <div class="bw-input__wrapper">
      <span v-if="prefixIcon || $slots.prefix" class="bw-input__prefix">
        <slot name="prefix">
          <i :class="prefixIcon"></i>
        </slot>
      </span>
      
      <input
        ref="inputRef"
        :class="['bw-input__inner', { 'has-prefix': prefixIcon || $slots.prefix, 'has-suffix': suffixIcon || $slots.suffix }]"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :maxlength="maxlength"
        @input="handleInput"
        @change="handleChange"
        @focus="handleFocus"
        @blur="handleBlur"
      />
      
      <span v-if="suffixIcon || $slots.suffix" class="bw-input__suffix">
        <slot name="suffix">
          <i :class="suffixIcon"></i>
        </slot>
      </span>
      
      <span v-if="clearable && modelValue" class="bw-input__clear" @click="handleClear">
        ✕
      </span>
    </div>
    
    <div v-if="error" class="bw-input__error">
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  modelValue: [String, Number],
  type: {
    type: String,
    default: 'text'
  },
  label: String,
  placeholder: String,
  prefixIcon: String,
  suffixIcon: String,
  disabled: Boolean,
  readonly: Boolean,
  clearable: Boolean,
  required: Boolean,
  error: String,
  maxlength: Number
})

const emit = defineEmits(['update:modelValue', 'change', 'focus', 'blur', 'clear'])

const inputRef = ref(null)

const handleInput = (event) => {
  emit('update:modelValue', event.target.value)
}

const handleChange = (event) => {
  emit('change', event.target.value)
}

const handleFocus = (event) => {
  emit('focus', event)
}

const handleBlur = (event) => {
  emit('blur', event)
}

const handleClear = () => {
  emit('update:modelValue', '')
  emit('clear')
  inputRef.value?.focus()
}

defineExpose({
  focus: () => inputRef.value?.focus(),
  blur: () => inputRef.value?.blur()
})
</script>

<style scoped>
.bw-input {
  width: 100%;
}

.bw-input__label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.bw-input__required {
  color: #ff4d4f;
  margin-left: 2px;
}

.bw-input__wrapper {
  position: relative;
  display: flex;
  align-items: center;
  background: var(--bg-elevated);
  border: 1px solid var(--border-secondary);
  border-radius: 6px;
  transition: all var(--transition-fast);
}

.bw-input__wrapper:hover:not(.is-disabled) {
  border-color: var(--border-primary);
}

.bw-input__wrapper:focus-within {
  border-color: var(--text-primary);
  box-shadow: 0 0 0 2px var(--border-primary);
}

.bw-input__inner {
  flex: 1;
  width: 100%;
  padding: 8px 12px;
  background: transparent;
  border: none;
  outline: none;
  color: var(--text-primary);
  font-size: 14px;
  line-height: 1.5;
}

.bw-input__inner.has-prefix {
  padding-left: 36px;
}

.bw-input__inner.has-suffix {
  padding-right: 36px;
}

.bw-input__inner::placeholder {
  color: var(--text-disabled);
}

.bw-input__inner:disabled {
  cursor: not-allowed;
  color: var(--text-disabled);
}

.bw-input__prefix,
.bw-input__suffix {
  position: absolute;
  display: flex;
  align-items: center;
  color: var(--text-tertiary);
  font-size: 14px;
}

.bw-input__prefix {
  left: 12px;
}

.bw-input__suffix {
  right: 12px;
}

.bw-input__clear {
  position: absolute;
  right: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  color: var(--text-tertiary);
  font-size: 12px;
  cursor: pointer;
  transition: all var(--transition-fast);
  border-radius: 50%;
  background: var(--bg-tertiary);
}

.bw-input__clear:hover {
  color: var(--text-primary);
  background: var(--bg-secondary);
}

.bw-input__error {
  margin-top: 6px;
  font-size: 12px;
  color: #ff4d4f;
  line-height: 1.4;
}

.bw-input.is-disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.bw-input.is-disabled .bw-input__wrapper {
  background: var(--bg-tertiary);
}
</style>
