import { useState, useRef, useCallback } from 'react'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export function useOCR(customerRecord = {}) {
  const [result,     setResult]     = useState(null)
  const [isLoading,  setIsLoading]  = useState(false)
  const [error,      setError]      = useState(null)
  const videoRef     = useRef(null)
  const streamRef    = useRef(null)

  // Open camera
  const openCamera = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment', width: 1280, height: 720 }
      })
      streamRef.current = stream
      if (videoRef.current) videoRef.current.srcObject = stream
    } catch (err) {
      setError('Camera access denied: ' + err.message)
    }
  }, [])

  // Capture snapshot and send to GPT-4o Vision
  const captureAndAnalyze = useCallback(async (docType = 'aadhaar') => {
    setIsLoading(true)
    setError(null)

    try {
      // Capture frame from video
      const canvas  = document.createElement('canvas')
      const video   = videoRef.current
      canvas.width  = video.videoWidth
      canvas.height = video.videoHeight
      canvas.getContext('2d').drawImage(video, 0, 0)

      // Convert to blob
      const blob = await new Promise(res => canvas.toBlob(res, 'image/jpeg', 0.92))

      const formData = new FormData()
      formData.append('image',           blob, 'document.jpg')
      formData.append('doc_type',        docType)
      formData.append('customer_record', JSON.stringify(customerRecord))

      const res = await axios.post(`${API_URL}/api/ocr/analyze`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      setResult(res.data)
      return res.data

    } catch (err) {
      const msg = err.response?.data?.detail || err.message
      setError(msg)
      return null
    } finally {
      setIsLoading(false)
    }
  }, [customerRecord])

  // Upload image file instead of camera
  const analyzeFile = useCallback(async (file, docType = 'aadhaar') => {
    setIsLoading(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('image',           file)
      formData.append('doc_type',        docType)
      formData.append('customer_record', JSON.stringify(customerRecord))

      const res = await axios.post(`${API_URL}/api/ocr/analyze`, formData)
      setResult(res.data)
      return res.data
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
      return null
    } finally {
      setIsLoading(false)
    }
  }, [customerRecord])

  const closeCamera = useCallback(() => {
    streamRef.current?.getTracks().forEach(t => t.stop())
    streamRef.current = null
  }, [])

  const clearResult = useCallback(() => setResult(null), [])

  return {
    result, isLoading, error,
    videoRef, openCamera, closeCamera,
    captureAndAnalyze, analyzeFile, clearResult,
  }
}