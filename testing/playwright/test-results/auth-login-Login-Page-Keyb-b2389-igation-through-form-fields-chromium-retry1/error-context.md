# Page snapshot

```yaml
- generic [ref=e6]:
  - generic [ref=e7]:
    - heading "irStudy" [level=1] [ref=e8]
    - paragraph [ref=e9]: Medical Education Platform
  - generic [ref=e10]:
    - generic [ref=e11]:
      - generic: Email Address
      - generic [ref=e12]:
        - textbox "Email Address" [ref=e13]
        - group:
          - generic: Email Address
      - paragraph [ref=e14]: Email is required
    - generic [ref=e15]:
      - generic: Password
      - generic [ref=e16]:
        - textbox "Password" [ref=e17]
        - group:
          - generic: Password
      - paragraph [ref=e18]: Password is required
    - generic [ref=e19] [cursor=pointer]:
      - generic [ref=e20]:
        - checkbox "Remember me" [ref=e21]
        - img [ref=e22]
      - generic [ref=e24]: Remember me
    - link "Forgot password?" [active] [ref=e26] [cursor=pointer]:
      - /url: /forgot-password
    - button "Sign In" [disabled]
    - paragraph [ref=e28]:
      - text: Don't have an account?
      - link "Sign up here" [ref=e29] [cursor=pointer]:
        - /url: /register
```