import type { ValidationRule } from './AuthInput.vue'

// ==================== Predefined Validation Rules ====================

export const predefinedRules = {
  /**
   * Required field validation
   */
  required: (message: string = '此项为必填项'): ValidationRule => ({
    validator: (value: string | number) => {
      if (typeof value === 'number') return !isNaN(value)
      return !!value?.toString().trim()
    },
    message,
    trigger: 'blur'
  }),

  /**
   * Email validation
   */
  email: (message: string = '请输入有效的邮箱地址'): ValidationRule => ({
    validator: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
    message,
    trigger: 'blur'
  }),

  /**
   * Phone number validation (China)
   */
  phone: (message: string = '请输入有效的手机号码'): ValidationRule => ({
    validator: /^1[3-9]\d{9}$/,
    message,
    trigger: 'blur'
  }),

  /**
   * Minimum length validation
   */
  minLength: (length: number, message?: string): ValidationRule => ({
    validator: (value: string | number) => String(value).length >= length,
    message: message || `至少需要 ${length} 个字符`,
    trigger: 'blur'
  }),

  /**
   * Maximum length validation
   */
  maxLength: (length: number, message?: string): ValidationRule => ({
    validator: (value: string | number) => String(value).length <= length,
    message: message || `不能超过 ${length} 个字符`,
    trigger: 'input'
  }),

  /**
   * Minimum value validation (for number input)
   */
  min: (min: number, message?: string): ValidationRule => ({
    validator: (value: string | number) => Number(value) >= min,
    message: message || `最小值为 ${min}`,
    trigger: 'input'
  }),

  /**
   * Maximum value validation (for number input)
   */
  max: (max: number, message?: string): ValidationRule => ({
    validator: (value: string | number) => Number(value) <= max,
    message: message || `最大值为 ${max}`,
    trigger: 'input'
  }),

  /**
   * URL validation
   */
  url: (message: string = '请输入有效的网址'): ValidationRule => ({
    validator: /^(https?:\/\/)?([\w-]+\.)+[\w-]+(\/[\w-.\/?%&=]*)?$/,
    message,
    trigger: 'blur'
  }),

  /**
   * Chinese character validation
   */
  chinese: (message: string = '只能包含中文字符'): ValidationRule => ({
    validator: /^[\u4e00-\u9fa5]+$/,
    message,
    trigger: 'input'
  }),

  /**
   * English character validation
   */
  english: (message: string = '只能包含英文字符'): ValidationRule => ({
    validator: /^[a-zA-Z]+$/,
    message,
    trigger: 'input'
  }),

  /**
   * Alphanumeric validation
   */
  alphanumeric: (message: string = '只能包含字母和数字'): ValidationRule => ({
    validator: /^[a-zA-Z0-9]+$/,
    message,
    trigger: 'input'
  }),

  /**
   * Special character validation (forbidden)
   */
  noSpecialChars: (message: string = '不能包含特殊字符'): ValidationRule => ({
    validator: /^[a-zA-Z0-9\u4e00-\u9fa5]+$/,
    message,
    trigger: 'input'
  }),

  /**
   * Password strength validation
   * At least 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special char
   */
  passwordStrength: (message: string = '密码需包含大小写字母、数字和特殊字符，且不少于8位'): ValidationRule => ({
    validator: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]).{8,}$/,
    message,
    trigger: 'input'
  }),

  /**
   * ID card number validation (China)
   */
  idCard: (message: string = '请输入有效的身份证号码'): ValidationRule => ({
    validator: /^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[1-2]\d|3[0-1])\d{3}(\d|X)$/i,
    message,
    trigger: 'blur'
  }),

  /**
   * Postal code validation (China)
   */
  postalCode: (message: string = '请输入有效的邮政编码'): ValidationRule => ({
    validator: /^[1-9]\d{5}$/,
    message,
    trigger: 'blur'
  })
}

// ==================== Validation Helpers ====================

export function validateEmail(value: string): boolean {
  return /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(value)
}

export function validatePhone(value: string): boolean {
  return /^1[3-9]\d{9}$/.test(value)
}

export function validateUrl(value: string): boolean {
  return /^(https?:\/\/)?([\w-]+\.)+[\w-]+(\/[\w-.\/?%&=]*)?$/.test(value)
}

export function validateChinese(value: string): boolean {
  return /^[\u4e00-\u9fa5]+$/.test(value)
}

export function validateAlphanumeric(value: string): boolean {
  return /^[a-zA-Z0-9]+$/.test(value)
}

export function validatePasswordStrength(value: string): boolean {
  return /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]).{8,}$/.test(value)
}

// ==================== Common Rule Sets ====================

export const authRules = {
  email: [
    predefinedRules.required(),
    predefinedRules.email()
  ],
  password: [
    predefinedRules.required(),
    predefinedRules.minLength(8, '密码至少8位'),
    predefinedRules.maxLength(32, '密码最多32位')
  ],
  username: [
    predefinedRules.required(),
    predefinedRules.minLength(3, '用户名至少3位'),
    predefinedRules.maxLength(20, '用户名最多20位'),
    predefinedRules.alphanumeric('用户名只能包含字母和数字')
  ],
  phone: [
    predefinedRules.required(),
    predefinedRules.phone()
  ]
}

// ==================== Default Export ====================
export default predefinedRules
