export function isMobile() {
  const userAgent = navigator.userAgent
  const mobileRegex = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i
  return mobileRegex.test(userAgent)
}

export function getDeviceType() {
  return isMobile() ? 'mobile' : 'pc'
}