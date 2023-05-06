import sys
import json
import copy

needsValueID = [
  "MultipleChoice",
  "TextInput",
  "Counter",
]

def missingErrorMessage(type: str, prop: str) -> str:
  if prop == "pageID" or prop == "valueID":
    return f"{type.capitalize()} is missing a unique identifier!"
  else:
    return f"{type.capitalize()} requires {prop} property!"

# Verifies that the given ID property is unique given a set
# of possible ID values. Beware: modifies the provided set!
def ensureUniqueID(type: str, obj, prop: str, IDs: set, required: bool):
  if prop in obj:
    value = obj[prop]
    if value in IDs:
      IDs.discard(value)
    else:
      obj[prop] = f"Duplicate {prop} detected!"
  elif required:
    obj[prop] = missingErrorMessage(type, prop)

# Verifies the the property on the given object is an actual
# identifier in use somewhere. Supports optional properties.
def isValidID(type: str, obj, prop: str, IDs: set, required: bool):
  if prop in obj:
    value = obj[prop]
    if value not in IDs:
      obj[prop] = f"Provided {prop} is not used by any page/component."
  elif required:
    obj[prop] = missingErrorMessage(type, prop)

# =========================== #
# PAGE & COMPONENT VALIDATION #

def validatePageObj(originalPage, validatedPage, pageIDs: set, unusedPageIDs: set):
  ensureUniqueID("page", validatedPage, "pageID", unusedPageIDs, True)
  isValidID("page", validatedPage, "defaultLink", pageIDs, True)

  if originalPage["defaultLink"] == originalPage["pageID"]:
    validatedPage["defaultLink"] = "Page should not link to itself!"
  
  if "title" not in originalPage:
    validatedPage["title"] = missingErrorMessage("page", "title")
  
  if "content" not in originalPage:
    validatedPage["content"] = missingErrorMessage("page", "content")

def validateComponentObj(originalComponent, validatedComponent, valueIDs: set, unusedValueIDs: set):
  componentType = originalComponent["component"]
  ensureUniqueID(componentType, validatedComponent, "valueID", unusedValueIDs, componentType in needsValueID)

# Takes a workflow object and returns a tuple with two contents.
# The first is a set of all page IDs and the second a set of all
# value IDs. Also takes an optional artifact parameter, this is an
# object which stores validation errors. 
def getAllIdentifiers(workflow, artifact):
  pageIDs = set()
  valueIDs = set()
  
  for pageIndex in range(len(workflow["pages"])):
    page = workflow["pages"][pageIndex]

    if "pageID" in page:
      pageIDs.add(page["pageID"])
    else:
      artifact["pageID"] = missingErrorMessage("page", "pageID")
    
    for componentIndex in range(len(page["content"])):
      component = page["content"][componentIndex]

      if "valueID" in component:
        valueIDs.add(component["valueID"])
      elif component["component"] in needsValueID:
        workflow["content"][componentIndex]["valueID"] = missingErrorMessage("component", "valueID")
  
  return pageIDs, valueIDs

# Validates the given workflow, returning an json-style object where
# properties map to error messages. Does not mutate the input workflow.
def validateWorkflow(workflow):
  artifact = copy.deepcopy(workflow)
  
  pageIDs, valueIDs = getAllIdentifiers(workflow, True)

  unusedPageIDs = copy.copy(pageIDs)
  unusedValueIDs = copy.copy(valueIDs)

  for pageIndex in range(len(workflow["pages"])):
    originalPage = workflow["pages"][pageIndex]
    validatedPage = artifact["pages"][pageIndex]

    validatePageObj(originalPage, validatedPage, pageIDs, unusedPageIDs)

    for componentIndex in range(len(originalPage["content"])):
      originalComponent = originalPage["content"][componentIndex]
      validatedComponent = validatedPage["content"][componentIndex]

      validateComponentObj(originalComponent, validatedComponent, valueIDs, unusedValueIDs)

  return artifact

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
    artifact = validateWorkflow(data)
    
    print(f"Writing validation artifact to '{sys.argv[2]}'")
    with open(sys.argv[2], 'w') as file:
      json.dump(artifact, file)