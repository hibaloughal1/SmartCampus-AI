import React from 'react'

export default function Spinner({ size = 20, className = '' }) {
  return (
    <div
      className={`animate-spin rounded-full border-2 border-ink/20 border-t-amber ${className}`}
      style={{ width: size, height: size }}
    />
  )
}
