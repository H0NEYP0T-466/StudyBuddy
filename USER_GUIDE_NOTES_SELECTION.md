# 📚 Quick Start Guide: Notes Selection Feature

## What's New?

The AI Assistant (Isabella) now lets you select specific notes to use as context for your conversations!

---

## 🎯 How to Use

### Step 1: Open AI Assistant
1. Click on the Isabella (🤖) icon in the navigation
2. Notice: "Use RAG" is now **checked by default** ✓

### Step 2: Open Notes Context Panel
1. Click the **📚 button** in the top right
2. The Notes Context panel will slide open on the right side

### Step 3: Select Subject Folders
1. Check the folders/subjects you want to include
2. Example: Check "Mathematics" and "Physics"
3. All notes in these folders will load automatically

### Step 4: Select Specific Notes
1. Use the **🔍 search box** to filter notes
   - Type "calculus" to find all calculus-related notes
   - Search works on both title and content
2. Check individual notes you want to include
   - Each note shows a preview of its content
3. Use quick actions:
   - Click **✓ Select All** to select all visible notes
   - Click **✗ Clear** to deselect everything

### Step 5: Ask Questions
1. Type your question in the chat
2. The AI will use your selected notes as context
3. See sources at the bottom showing which notes/documents were used

---

## 💡 Examples

### Example 1: Study Help
```
1. Select folder: "Biology"
2. Search: "cell structure"
3. Select: Cell Structure.txt, Organelles.txt
4. Ask: "Explain the difference between prokaryotic and eukaryotic cells"
```
→ AI will answer using your specific notes on cell structure

### Example 2: Homework Help
```
1. Select folder: "Mathematics"
2. Search: "derivatives"
3. Select all notes about derivatives
4. Ask: "How do I solve this derivative problem?"
```
→ AI has full context from your derivative notes

### Example 3: Exam Prep
```
1. Select folders: "History", "Political Science"
2. Don't search - Select All to include everything
3. Ask: "Give me a practice quiz on World War II"
```
→ AI uses all your notes to create relevant questions

---

## 🎨 UI Elements

### Notes Context Panel

```
┌─────────────────────────────────────┐
│ 📚 Notes Context                    │
│ Step 1: Select subjects             │
├─────────────────────────────────────┤
│ Folders:                            │
│ ☑️ Mathematics                       │
│ ☑️ Physics                           │
│ ☐ Chemistry                         │
├─────────────────────────────────────┤
│ 📄 Select Notes (5/10 selected)     │
│ [✓ Select All] [✗ Clear]           │
│                                     │
│ 🔍 Search notes...                  │
├─────────────────────────────────────┤
│ ☑️ Calculus Basics                  │
│    Derivatives and integrals...     │
│                                     │
│ ☑️ Linear Algebra                   │
│    Matrices and vector spaces...    │
│                                     │
│ ☐ Trigonometry                      │
│    Sin, cos, tan functions...       │
└─────────────────────────────────────┘
```

### Sources Display

After AI responds, you'll see sources like this:

```
📚 Sources: [Calculus Basics] [Linear Algebra] [machine_learning.txt]
           └─ Your notes ─┘  └───────── RAG documents ────────┘
```

### Info Display

At the bottom of the chat:
```
[Model: Gemini 2.5 Flash] ☑️ Use RAG  ☐ Isolate Message
2 folders, 5 notes selected
```

---

## 🔧 Tips & Tricks

### Tip 1: Combine RAG + Selected Notes
- **Best Practice**: Use both RAG and note selection together
- RAG finds relevant document chunks automatically
- Selected notes provide complete context
- Result: Most comprehensive and accurate answers

### Tip 2: Search Before Selecting
- Don't waste time scrolling through many notes
- Use search to quickly find what you need
- Search is case-insensitive and instant

### Tip 3: Select All for Broad Topics
- Studying for comprehensive exams?
- Click "Select All" to include everything
- AI will have full context from all your notes

### Tip 4: Be Specific for Homework
- Working on a specific problem?
- Select only relevant notes
- More focused context = better answers

### Tip 5: Use Isolate Message for Testing
- Want to test if AI knows something without your notes?
- Check "Isolate Message"
- AI won't use conversation history or notes

---

## ❓ FAQ

### Q: What's the difference between RAG and selected notes?
**A**: 
- **RAG**: Automatically searches all documents in `backend/data/` and finds relevant chunks
- **Selected Notes**: You manually choose which complete notes to include
- **Together**: Best of both worlds!

### Q: How many notes can I select?
**A**: No hard limit, but be mindful:
- More notes = more context tokens used
- Consider your model's token limit
- Usually 5-10 notes is sufficient

### Q: Do I need to select notes every time?
**A**: No! Your selection persists during your session. When you switch folders or deselect all, the selection resets.

### Q: What if I can't find a note in search?
**A**: Make sure:
1. The folder containing the note is selected
2. Check your search spelling
3. Try searching part of the title or content

### Q: Can I see the full note content?
**A**: Currently you see a 60-character preview. Click on the note in the Notes Library to view the full content.

---

## 🚀 Advanced Usage

### Workflow 1: Research Mode
```
1. Select multiple subject folders
2. Don't filter - Select All
3. Ask broad research questions
4. AI draws from comprehensive context
```

### Workflow 2: Problem-Solving Mode
```
1. Select one specific folder
2. Search for problem-related keywords
3. Select 2-3 most relevant notes
4. Ask specific question about the problem
```

### Workflow 3: Review Mode
```
1. Select exam-relevant folders
2. Select All notes
3. Ask for summaries and practice questions
4. Use sources to see which topics were covered
```

---

## 🎓 Why This Feature is Powerful

### Before
- AI had access to RAG chunks only
- No control over what context was used
- Sometimes missed relevant notes

### After
- **You control** exactly what the AI sees
- **Search** to find relevant notes quickly
- **Combine** with RAG for comprehensive answers
- **See sources** - know what was used
- **Precise answers** from your specific study materials

---

## 🐛 Troubleshooting

### Issue: Notes panel won't open
- **Solution**: Click the 📚 button in the top-right corner

### Issue: No notes showing after selecting folder
- **Solution**: That folder might be empty. Add notes to it first.

### Issue: Search returns no results
- **Solution**: 
  - Check if the folder is selected
  - Try different keywords
  - Clear search and manually browse

### Issue: Sources not showing
- **Solution**: Make sure "Use RAG" is checked and you have notes selected

---

## 📞 Need More Help?

Check the comprehensive documentation:
- `FEATURE_NOTES_SELECTION.md` - Technical details
- `CHANGES_SUMMARY_DETAILED.md` - What changed
- `README.md` - Full application guide

---

Happy studying! 🎓✨
