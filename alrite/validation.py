import sys
import json
import copy
from typing import Tuple

needsValueID = [
  "MultipleChoice",
  "TextInput",
  "Counter",
]

componentProps = {
  # True means prop is required,
  # False means prop may be omitted.

  "Paragraph": {
    "text": True,
  },
  "MediaItem": {
    "fileName": True,
    "label": False
  },
  "MultipleChoice": {
    "label": True,
    "valueID": True,
    "multiselect": True,
  },
  "Choice": {
    "text": True,
    "value": True,
    "link": False,
  },
  "TextInput": {
    "label": True,
    "type": True,
    "valueID": True,
    "units": False,
    "defaultValue": False,
  },
  "Button": {
    "text": True,
    "hint": False,
    "link": True,
  },
  "Counter": {
    "title": True,
    "hint": False,
    "timeLimit": True,
    "valueID": True,
    "offerManualInput": True,
  },

  "Comparison": {
    "type": True,
    "threshold": True,
    "targetValueID": True,
    "satisfiedLink": True,
  },
  "Selection": {
    "type": True,
    "targetValueID": True,
    "satisfiedLink": True,
  },
  "Validation": {
    "type": True,
    "threshold": True,
    "targetValueID": True,
  },
}

# ================ #
# HELPER FUNCTIONS #
# ================ #

def missingErrorMessage(prop: str, type: str = None) -> str:
  if prop == "pageID" or prop == "valueID":
    if type is None:
      return f"A unique identifier is required!"
    else:
      return f"{type.capitalize()} is missing a unique identifier!"
  else:
    if type is None:
      return f"The {prop} property is required!"
    else:
      return f"{type.capitalize()} requires {prop} property!"

def hasValidPropertyValue(component, prop, valid):
  return prop in component and component[prop] in valid

def dictCompare(d1, d2):
  d1_keys = set(d1.keys())
  d2_keys = set(d2.keys())
  shared_keys = d1_keys.intersection(d2_keys)
  
  added = d1_keys - d2_keys
  removed = d2_keys - d1_keys
  modified = {o for o in shared_keys if d1[o] != d2[o]}
  # modified = {o : (d1[o], d2[o]) for o in shared_keys if d1[o] != d2[o]}
  same = set(o for o in shared_keys if d1[o] == d2[o])
  return added, removed, modified, same

def listToReadableString(lst):
  string = ""
  for elem in lst:
    string += " " + elem + ","
  return string[:-1]

def readablePositionString(num):
  if num == 0:
    return "1st"
  elif num == 1:
    return "2nd"
  elif num == 2:
    return "3rd"
  else:
    return f"{num + 1}th"

# ================ #
# WORKFLOW CLASSES #
# ================ #

# ---- #
# PAGE #
class PageEncoder(json.JSONEncoder):
  def default(self, obj):
    return obj.__dict__ 

class Page():
  def __init__(self, pageID, rawPage = None):
    self.pageID = pageID

    self.defaultLink: str = rawPage["defaultLink"] if rawPage is not None else None
    self.isDiagnosisPage: bool = rawPage["isDiagnosisPage"] if rawPage is not None else None
    self.title: str = rawPage["title"] if rawPage is not None else None
    self.content: list = rawPage["content"] if rawPage is not None else []

    # Pages can have error information that isn't specific to a prop (unused page)
    # or we can't store in the prop (pageID) so we use this instead.
    self.pageError = None
  
  def __str__(self):
    return json.dumps(self.__dict__, ensure_ascii=False)

  def appendComponent(self, component: dict):
    self.content.append(component)
# PAGE #
# ---- #

class Workflow:
  def __init__(self, workflow):
    self.name = workflow["name"]
    self.rawWorkflow = workflow
    
    self.valid = True
    self.artifact = WorkflowArtifact(workflow)
    
    self.pages: list(Page) = self._extractPageData()  
    self.indexMap: map(str, int) = self._createPageIdentifierMap()

    self.pageIDs, self.valueIDs = self._getAllIdentifiers()

  def __iter__(self):
    return WorkflowIter(self.pages)

  # ================= #
  # PARSING FUNCTIONS #
  # ================= #

  def _extractPageData(self):
    pages = []

    for pageIndex in range(len(self.rawWorkflow["pages"])):
      rawPage = self.rawWorkflow["pages"][pageIndex]
      pages.append(Page(rawPage["pageID"], rawPage))
    
    return pages

  # Returns a map which provides pageID -> pageIndex.
  def _createPageIdentifierMap(self):
    map = {}
    for pageIndex in range(len(self.pages)):
      map[self.pages[pageIndex].pageID] = pageIndex
    return map
  
  def _getAllIdentifiers(self):
    pageIDs = set()
    valueIDs = set()
    
    for wPage in self.pages:
      aPage = self.getArtifactPage(wPage.pageID)
      pageIDs.add(wPage.pageID)

      for componentIndex in range(len(wPage.content)):
        component = wPage.content[componentIndex]

        if "valueID" in component:
          valueIDs.add(component["valueID"])
        elif component["component"] in needsValueID:
          aPage.content[componentIndex]["valueID"] = missingErrorMessage("valueID", "component")
    
    return pageIDs, valueIDs

  # ================ #
  # HELPER FUNCTIONS #
  # ================ #

  # Returns the target page, which may be a 
  # pageID string or an integer page index.
  def getPage(self, target) -> Page:
    if isinstance(target, str):
      pageIndex = self.indexMap[target]
    elif isinstance(target, int):
      pageIndex = target
    return self.pages[pageIndex]

  def hasPage(self, target) -> bool:
    if isinstance(target, str):
      return target in self.indexMap
    elif isinstance(target, int):
      return target > 0 and target < len(self.pages)
  
  def getArtifactPage(self, target) -> Page:
    if isinstance(target, str):
      pageIndex = self.indexMap[target]
    elif isinstance(target, int):
      pageIndex = target
    return self.artifact.pages[pageIndex]
  
  # ==================== #
  # VALIDATION FUNCTIONS #
  # ==================== #

  def validate(self):
    self.valid = True
    unusedPageIDs, unusedValueIDs = copy.copy(self.pageIDs), copy.copy(self.valueIDs)

    for wPage in self.pages:
      self.validatePageObj(wPage.pageID, unusedPageIDs)

      for componentIndex in range(len(wPage.content)):
        self.validateComponentObj(wPage.pageID, componentIndex, unusedValueIDs)

    self.searchForUnusedAndLoops()
    return self.valid
  
  def validatePageObj(self, target, unusedPageIDs: set):
    originalPage = self.getPage(target)
    artifactPage = self.getArtifactPage(target)

    self.valid = self.valid and self.ensureUniquePageID(originalPage, artifactPage, unusedPageIDs)
    self.valid = self.valid and self.isValidID(originalPage, artifactPage, "defaultLink", self.pageIDs, True)

    if originalPage.defaultLink == originalPage.pageID:
      artifactPage.defaultLink = "Page should not link to itself!"
      self.valid = False

  # Verifies that the given ID property is unique given a set
  # of possible ID values. Beware: modifies the provided set!
  def ensureUniquePageID(self, originalPage, artifactPage, unusedIDs: set):
    if originalPage.pageID in unusedIDs:
      unusedIDs.discard(originalPage.pageID)
      return True
    else:
      # We don't store this in the pageID since the front end uses
      # IDs to distinguish pages, so the artifact should not modify IDs.
      artifactPage.pageError = f"Duplicate pageID detected!"
      return False
    
  def validateComponentObj(self, targetPage, componentIndex, unusedValueIDs: set):
    originalPage = self.getPage(targetPage)
    artifactPage = self.getArtifactPage(targetPage)

    originalComponent = originalPage.content[componentIndex]
    artifactComponent = artifactPage.content[componentIndex]
    componentType = originalComponent["component"]

    isUnique, errorMessage = self.ensureUniqueID(componentType, originalComponent, "valueID", unusedValueIDs, componentType in needsValueID)
    if not isUnique:
      self.valid = False
      artifactComponent["valueID"] = errorMessage

    if "link" in originalComponent and originalComponent["link"] == originalPage.pageID:
      artifactComponent["link"] = "Component should link to a different page!"
      self.valid = False

    if componentType == "TextInput" and not hasValidPropertyValue(originalComponent, "type", ["numeric", "alphanumeric", "text", "any"]):
      artifactComponent["type"] = f"Invalid input type provided."
      self.valid = False

    if componentType in ["Comparison", "Validation"] and not hasValidPropertyValue(originalComponent, "type", [">", "<", ">=", "<=", "="]):
      artifactComponent["type"] = f"Invalid comparison type provided."
      self.valid = False

    if componentType == "Selection" and not hasValidPropertyValue(originalComponent, "type", ["all_selected", "at_least_one", "exactly_one", "none_selected"]):
      artifactComponent["type"] = f"Invalid selection type provided."
      self.valid = False

    self.valid = self.valid and self.isValidID(originalComponent, artifactComponent, "targetValueID", self.valueIDs, False)

    if "choices" in originalComponent:
      for choiceIndex in range(len(originalComponent["choices"])):
          originalChoice = originalComponent["choices"][choiceIndex]
          artifactChoice = artifactComponent["choices"][choiceIndex]
          self.ensureRequiredProps(originalChoice, artifactChoice, "Choice")

    self.ensureRequiredProps(originalComponent, artifactComponent, componentType)

  def ensureRequiredProps(self, original, artifact, type):
    for prop, required in componentProps[type].items():
      if required and (prop not in original or original[prop] == ""):
        artifact[prop] = f"Component is missing {prop} property!"
        self.valid = False
  
  # Verifies that the given ID property is unique given a set
  # of possible ID values. Beware: modifies the provided set!
  def ensureUniqueID(self, type: str, original: dict, prop: str, unusedIDs: set, required: bool):# -> tuple[bool, str]:
    if prop in original:
      value = original[prop]
      if value in unusedIDs:
        unusedIDs.discard(value)
        return True, None
      else:
        return False, f"Duplicate {prop} detected!"
    elif required:
      return False, missingErrorMessage(type, prop)
    else:
      return True, None
    
  # Verifies the the property on the given page or component is an actual identifier
  # in use somewhere. Supports optional properties, on both components and pages
  def isValidID(self, original, artifact, prop: str, values: list, required: bool):
    if isinstance(original, Page):
      return self._checkPageHasValidID(original, artifact, prop, values, required)
    else:
      return self._checkComponentHasValidID(original, artifact, prop, values, required)
    
  def _checkPageHasValidID(self, original, artifact, prop: str, values: list, required: bool):
    if hasattr(original, prop):
      value = getattr(original, prop)
      if value in values:
        return True
      else:
        setattr(artifact, prop, f"Provided {prop} is not used by any page/component.")
        return False
    elif required:
      setattr(artifact, prop, missingErrorMessage(prop, "page"))
      return False
    else:
      return True
      
  def _checkComponentHasValidID(self, original, artifact, prop: str, values: list, required: bool):
    if prop in original:
      value = original[prop]
      if value in values:
        return True
      else:
        artifact[prop] = f"Provided {prop} is not used by any page/component."
        return False
    elif required:
      artifact[prop] = missingErrorMessage(prop, "component")
      return False
    else:
      return True
    
  def searchForUnusedAndLoopsHelper(self, targetPage: str, visitedPages: set, noneOkay: bool = False):# -> tuple[str, set]:
    try:
      currPage: Page = self.getPage(targetPage)
    except KeyError:
      if not noneOkay:
        self.valid = False
        return "None or invalid pageID provided!", visitedPages
      else:
        return None, visitedPages
    
    seenPages = set(visitedPages)
    visitedPages = set(visitedPages)

    if currPage.pageID in visitedPages:
      seenPages.add(currPage.pageID)
      self.valid = False
      return "Workflow loops back on itself!", seenPages
    else:
      visitedPages.add(currPage.pageID)
      seenPages.add(currPage.pageID)
      artifactPage = self.getArtifactPage(targetPage)

      if not currPage.isDiagnosisPage:
        error, visited = self.searchForUnusedAndLoopsHelper(currPage.defaultLink, visitedPages)
        if error != None: artifactPage.defaultLink = error
        seenPages.update(visited)

        for componentIndex in range(len(currPage.content)):
          originalComponent = currPage.content[componentIndex]
          artifactComponent = artifactPage.content[componentIndex]
          componentType = originalComponent["component"]

          if componentType == "MultipleChoice" and not originalComponent["multiselect"]:
            for choiceIndex in range(len(originalComponent["choices"])):
              choice = originalComponent["choices"][choiceIndex]

              error, visited = self.searchForUnusedAndLoopsHelper(choice["link"], visitedPages, True)
              if error != None: artifactComponent["choices"][choiceIndex]["link"] = error
              seenPages.update(visited)
          else:
            for prop in componentProps[componentType]:
              # If the prop is any kind of prop that could cause the
              # "Next" button to lead somewhere, it is a branch we must check.
              if prop in ["link", "satisfiedLink"]:
                error, visited = self.searchForUnusedAndLoopsHelper(originalComponent[prop], visitedPages)
                if error != None: artifactComponent[prop] = error
                seenPages.update(visited)
    
      return None, seenPages

  def searchForUnusedAndLoops(self):
    error, visited = self.searchForUnusedAndLoopsHelper(0, set())

    unused = self.pageIDs - visited
    for pageID in unused:
      self.getArtifactPage(pageID).pageError = "Unused page: nothing links to this page!"
      self.valid = False

  # =============== #
  # VERSION CHANGES #
  # =============== #

  def computeChanges(self, prev: "Workflow"):
    changesArtifact = WorkflowArtifact(self.rawWorkflow, True)

    for page in self.pages:
      changesPage: Page = changesArtifact.pages[self.indexMap[page.pageID]]

      if (prev.hasPage(page.pageID)):
        prevPage: Page = prev.getPage(page.pageID)

        if prevPage.title != page.title:
          changesPage.title = f"Page title was changed from \"{prevPage.title}\" to \"{page.title}\""

        if prevPage.defaultLink != page.defaultLink:
          linkTarget = self.getPage(page.defaultLink)
          prevLinkTarget = prev.getPage(prevPage.defaultLink)
          changesPage.defaultLink = f"Default link was changed from \"{prevLinkTarget.title}\" ({prevPage.defaultLink}) to \"{linkTarget.title}\" ({page.defaultLink})"
        
        if prevPage.isDiagnosisPage != page.isDiagnosisPage:
          changesPage.isDiagnosisPage = f"Is diagnosis page toggled to " + page.isDiagnosisPage

        for componentIndex in range(len(page.content)):
          component = page.content[componentIndex]

          if componentIndex < len(prevPage.content):
            prevComponent = prevPage.content[componentIndex]

            changeBase = f"The {readablePositionString(componentIndex)} component"
            if component["component"] != prevComponent["component"]:
              changesPage.content[componentIndex] = changeBase + f" was changed from {prevComponent['component']} to {component['component']}."
            elif component != prevComponent:
              added, removed, modified, same = dictCompare(component, prevComponent)
              changesPage.content[componentIndex] = changeBase + f" ({component['component']}) had the following props changed: {listToReadableString(modified)}"
          
          else:
            # The component didn't exist in the previous workflow.
            changesPage.appendComponent(f"New component of type {component['component']} added")
      
      else:
        # The page did not exist in the previous workflow.
        changesPage.pageError = f"New page, containing {len(page.content)} component(s)"

    for prevPage in prev.pages:
      if not self.hasPage(prevPage.pageID):
        # If the new workflow removed a page from the previous workflow,
        # we need a dummy page in the changes artifact enumerating this information.
        deletedPage = Page(prevPage.pageID)
        deletedPage.pageError = "Page was removed"
        changesArtifact.pages.append(deletedPage)

    return changesArtifact

class WorkflowIter:
  def __init__(self, pages):
    self.index = -1
    self.pages = pages

  def __iter__(self):
    return self

  def __next__(self):
    if (self.index + 1) < len(self.pages):
      self.index += 1
      return self.pages[self.index]
    else:
      raise StopIteration

class WorkflowArtifact:
  def __init__(self, workflow, noContent = False):
    self.pages = []

    for pageIndex in range(len(workflow["pages"])):
      originalPage = workflow["pages"][pageIndex]
      
      self.pages.append(Page(originalPage["pageID"]))
      validatedPage = self.pages[pageIndex]

      for componentIndex in range(len(originalPage["content"])):
        originalComponent = originalPage["content"][componentIndex]

        if not noContent:
          validatedComponent = { "component": originalComponent["component"] }
          
          if originalComponent["component"] == "MultipleChoice":
            validatedComponent["choices"] = [{
              "text": None,
              "value": None,
              "link": None,
            } for _ in range(len(originalComponent["choices"]))]

          validatedPage.content.append(validatedComponent)
        else:
          validatedPage.content.append("")

  def purgeUnchangedPages(self):
    def _pageWasChanged(page):
      pageChanged = False

      if page.defaultLink or page.isDiagnosisPage or page.title or page.pageError:
        pageChanged = True

      for component in page.content:
        if component != "":
          pageChanged = True

      return pageChanged

    self.pages = [page for page in self.pages if _pageWasChanged(page)]

  def getSerializable(self):
    return json.dumps(self.__dict__, cls=PageEncoder, ensure_ascii=False)
  
  def getJsonObj(self):
    def getobj(obj):
      if not  hasattr(obj,"__dict__"):
        return obj
      result = {}
      for key, val in obj.__dict__.items():
          if key.startswith("_"):
              continue
          element = []
          if isinstance(val, list):
              for item in val:
                  element.append(getobj(item))
          else:
              element = getobj(val)
          result[key] = element
      return result
    return getobj(self)

# =============== #
# MAIN VALIDATION #

# Validates the given workflow, returning an json-style object where
# properties map to error messages. Does not mutate the input workflow.
def validateWorkflow(rawWorkflow):
  workflow = Workflow(rawWorkflow)
  valid = workflow.validate()

  return workflow.artifact.getSerializable(), valid


# Given two workflows, returns a json-style object enumerating
# changes assuming workflowA came before workflowB, formatted like so:
# {
#   pages: [
#     {
#       pageID: The string page ID,
#       title: Boolean status whether the title was changed,
#       defaultLink: Boolean status whether the defaultLink was changed,
#       status: A string status "removed", "added", "modified, or "unchanged",
#       changes: Array of strings for each component, empty string if component wasn't
#                changed and a string description of the change if it was changed.
#     },
#     ...
#   ]
# }
def calculateChanges(rawWorkflowA, rawWorkflowB):
  workflowA = Workflow(rawWorkflowA)
  workflowB = Workflow(rawWorkflowB)

  changesArtifact = workflowB.computeChanges(workflowA)
  changesArtifact.purgeUnchangedPages()

  return changesArtifact.getJsonObj()

def getBrokenWorkflowErrorArtifact(rawWorkflow):
  return {
    "pages": [{
      "pageID": rawWorkflow["pages"][0]["pageID"],
      "pageError": "Catastrophic error: could not parse workflow. Contact system administrator.",
      "content": [],
    }],
    "status": "Catastrophic Error",
  }

# ============== #
# VALIDATION CLI #

def readWorkflowFromFile(path: str):
  with open(path, 'r') as file:
    workflow = json.load(file)

  print(f"Successfully loaded workflow '{workflow['name']}'\n")
  return workflow

if __name__ == "__main__":
  if (len(sys.argv) != 3):
    print(f"Wrong number of arguments, got {len(sys.argv) - 1}, expected 2")
    print("Usage: python validation.py {input file} {output file}")
    sys.exit()
  else:
    print(f"Reading workflow from '{sys.argv[1]}'")
    data = readWorkflowFromFile(sys.argv[1])
    artifact, valid = validateWorkflow(data)
    
    if valid: 
      print("Workflow valid!")
    else:
      print("Workflow invalid!")

    print(f"Writing validation artifact to '{sys.argv[2]}'")
    with open(sys.argv[2], 'w') as file:
      json.dump(artifact, file)
