# AuthInput Component

A comprehensive input component with validation, icons, and accessibility support.

## Features

- **Input Types**: text, password, email, number, tel
- **States**: default, focused, disabled, error, success
- **Icons**: prefix/suffix icons, password toggle, clear button
- **Validation**: built-in rules, custom validators
- **Accessibility**: ARIA labels, keyboard navigation, screen reader support
- **Dark Mode**: full support

## Usage

```vue
<script setup lang="ts">
import { ref } from 'vue'
import { AuthInput, authRules } from '@/components/auth'

const email = ref('')
const password = ref('')

const handleSubmit = () => {
  // Form submission
}
</script>

<template>
  <form @submit.prevent="handleSubmit">
    <AuthInput
      v-model="email"
      name="email"
      type="email"
      label="Email"
      placeholder="Enter your email"
      :rules="authRules.email"
      show-clear
    />

    <AuthInput
      v-model="password"
      name="password"
      type="password"
      label="Password"
      placeholder="Enter your password"
      :rules="authRules.password"
      show-password-toggle
    />
  </form>
</template>
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| modelValue | string \| number | '' | v-model binding value |
| type | 'text' \| 'password' \| 'email' \| 'number' \| 'tel' | 'text' | Input type |
| name | string | '' | Form field name |
| label | string | '' | Label text |
| placeholder | string | '' | Placeholder text |
| disabled | boolean | false | Disabled state |
| readonly | boolean | false | Readonly state |
| required | boolean | false | Required field |
| rules | ValidationRule[] | [] | Validation rules |
| status | 'default' \| 'error' \| 'success' | 'default' | Input status |
| size | 'sm' \| 'md' \| 'lg' | 'md' | Component size |
| rounded | 'none' \| 'sm' \| 'md' \| 'lg' \| 'full' | 'md' | Border radius |
| showClear | boolean | false | Show clear button |
| showPasswordToggle | boolean | false | Show password toggle |
| maxlength | number | - | Maximum character length |

## Validation Rules

```ts
import { predefinedRules } from '@/components/auth'

const rules = [
  predefinedRules.required('此项为必填'),
  predefinedRules.email('请输入有效的邮箱'),
  predefinedRules.minLength(8, '至少8个字符'),
  predefinedRules.maxLength(20, '最多20个字符'),
  predefinedRules.phone('请输入有效的手机号')
]
```

## Exposed Methods

- `focus()` - Focus the input
- `blur()` - Blur the input
- `validate()` - Run validation
- `clear()` - Clear the input value

## Form Integration

```ts
import { useForm } from '@/composables/useForm'

const { values, errors, handleSubmit } = useForm({
  email: '',
  password: ''
})
```
