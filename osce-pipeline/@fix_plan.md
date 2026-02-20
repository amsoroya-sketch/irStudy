# @fix_plan.md — OSCE Pipeline Processing Checklist

## Pipeline: 34 OSCE Videos → AMC Study Reports

**Instructions for Ralph**: Process each URL below sequentially.
Follow @AGENT.md rules. Mark [ ] → [x] when `report.html` + `report.md` exist for that video.

---

## Batch 1 — Videos 1–7

- [ ] 1. https://www.youtube.com/watch?v=wZK4uzwjcGE
- [ ] 2. https://www.youtube.com/watch?v=KW829pski4E
- [ ] 3. https://www.youtube.com/watch?v=4RIl263zJ7E
- [ ] 4. https://www.youtube.com/watch?v=7L3rP83KT8A
- [ ] 5. https://www.youtube.com/watch?v=O0yvsApLdd4
- [ ] 6. https://www.youtube.com/watch?v=PIXjQ8A474k
- [ ] 7. https://www.youtube.com/watch?v=NlBFzKlVVok

## Batch 2 — Videos 8–14

- [ ] 8.  https://www.youtube.com/watch?v=VZTAuTPIdbE
- [ ] 9.  https://www.youtube.com/watch?v=aj3dhhsGc2Y
- [ ] 10. https://www.youtube.com/watch?v=joKq9K-2SBY
- [ ] 11. https://www.youtube.com/watch?v=kKaG3VDxg1s
- [ ] 12. https://www.youtube.com/watch?v=pEzrBl3fmzI
- [ ] 13. https://www.youtube.com/watch?v=pfFxT1UNlFk
- [ ] 14. https://www.youtube.com/watch?v=tUmbol7Np44

## Batch 3 — Videos 15–20

- [ ] 15. https://www.youtube.com/watch?v=vFPBZQAxcDc
- [ ] 16. https://www.youtube.com/watch?v=0ztp4ZWVudk
- [ ] 17. https://www.youtube.com/watch?v=8bjLoq0iKnU
- [ ] 18. https://www.youtube.com/watch?v=LdJ4dq6ubJk
- [ ] 19. https://www.youtube.com/watch?v=abvlmyykE9E
- [ ] 20. https://www.youtube.com/watch?v=dtiPElaKITs

## Batch 4 — Videos 21–23

- [ ] 21. https://www.youtube.com/watch?v=tHEYpx7XI5Y
- [ ] 22. https://www.youtube.com/watch?v=ycesXdXRP3Q
- [ ] 23. https://www.youtube.com/watch?v=guebQEb3RNQ

## Batch 5 — Videos 24–28

- [ ] 24. https://www.youtube.com/watch?v=D46a4Mxc4AY
- [ ] 25. https://www.youtube.com/watch?v=GmN5OWCGXts
- [ ] 26. https://www.youtube.com/watch?v=Lp-9S960GB0
- [ ] 27. https://www.youtube.com/watch?v=V5sGZe1RdNs
- [ ] 28. https://www.youtube.com/watch?v=eXTIpyVvymc

## Batch 6 — Videos 29–34

- [ ] 29. https://www.youtube.com/watch?v=0a83jsF06zA
- [ ] 30. https://www.youtube.com/watch?v=TZF2zjYz-Sg
- [ ] 31. https://www.youtube.com/watch?v=bSH9Ygwikvk
- [ ] 32. https://www.youtube.com/watch?v=2gBHWM7BgPg
- [ ] 33. https://www.youtube.com/watch?v=DbOK6hPqXjk
- [ ] 34. https://www.youtube.com/watch?v=DogUXwhemAE

---

## Completion Criteria

Each URL is complete when:
- `output/{slug}/report.html` exists
- `output/{slug}/report.md` exists
- `output/{slug}/status.json` shows `"step": "complete"`

## Final Step

After all 34 are marked [x]:
- Run: `$MSDEV_VENV/bin/python scripts/09_index.py`
- Verify: `osce-pipeline/index.html` opens with all 34 cards
- Output: `RALPH_STATUS: PIPELINE_COMPLETE`
