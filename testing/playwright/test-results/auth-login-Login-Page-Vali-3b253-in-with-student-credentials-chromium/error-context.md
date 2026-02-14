# Page snapshot

```yaml
- generic [ref=e6]:
  - generic [ref=e7]:
    - heading "irStudy" [level=1] [ref=e8]
    - paragraph [ref=e9]: Medical Education Platform
  - alert [ref=e10]:
    - img [ref=e12]
    - generic [ref=e14]: Invalid credentials
  - generic [ref=e15]:
    - generic [ref=e16]:
      - generic [ref=e17]: Email Address
      - generic [ref=e18]:
        - textbox "Email Address" [ref=e19]: student@test.com
        - group:
          - generic: Email Address
    - generic [ref=e20]:
      - generic [ref=e21]: Password
      - generic [ref=e22]:
        - textbox "Password" [ref=e23]: Student123!@
        - group:
          - generic: Password
    - generic [ref=e24] [cursor=pointer]:
      - generic [ref=e25]:
        - checkbox "Remember me" [ref=e26]
        - img [ref=e27]
      - generic [ref=e29]: Remember me
    - link "Forgot password?" [ref=e31] [cursor=pointer]:
      - /url: /forgot-password
    - button "Sign In" [ref=e32] [cursor=pointer]: Sign In
    - paragraph [ref=e34]:
      - text: Don't have an account?
      - link "Sign up here" [ref=e35] [cursor=pointer]:
        - /url: /register
```