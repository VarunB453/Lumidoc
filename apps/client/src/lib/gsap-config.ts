import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { TextPlugin } from 'gsap/TextPlugin'
import { CustomEase } from 'gsap/CustomEase'

gsap.registerPlugin(ScrollTrigger, TextPlugin, CustomEase)

CustomEase.create('smooth.in', 'M0,0 C0.25,0 0.5,1 1,1')
CustomEase.create('smooth.out', 'M0,0 C0.5,0 0.75,1 1,1')
CustomEase.create(
  'elastic.soft',
  'M0,0 C0.14,0 0.242,1.415 0.272,1.415 0.394,1.415 0.32,1 1,1',
)
CustomEase.create('expo.out', 'M0,0 C0.16,1 0.3,1 1,1')
CustomEase.create('quart.out', 'M0,0 C0.25,1 0.5,1 1,1')

gsap.defaults({ ease: 'quart.out', duration: 0.6 })

export { gsap, ScrollTrigger }
