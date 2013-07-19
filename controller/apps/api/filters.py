import string
import sys

from django.db.models import Q
from django.core import exceptions
from django.core.exceptions  import FieldError
from django.db.models.fields import FieldDoesNotExist
from django.db.models.related import RelatedObject
from rest_framework import filters


DEBUG = False


class JSONPointerFilterBackend(filters.BaseFilterBackend):
    """
    Enables filtering by an arbitrary JSON pointer query parameter in the URL
    Other queries should be unaffected
    Throws JSONPointerException
    """
    def filter_queryset(self, request, queryset, view):
        if DEBUG:
            print "In JSONPointerFilterBackend.filter_queryset"
        querylist = request.QUERY_PARAMS                   	# the full query dictionary as passed on from the request
        
        if querylist is not None:
            for qitem, qvaluelist in querylist.iterlists():           # loop over queries; the filter results will be ANDed together
                if len(qvaluelist) != 1:                                  # QueryDict can contain more than one value per key, but of course we need exactly one
                    raise Exception("Invalid value assignation")
                ormlist = []                                                 # ormlist will contain all wildcard- (and qvalue-) matching paths converted to ORM lookup syntax
                if qitem.startswith(r'show'):                         # member selection keyword
                    pass
                else:
                    if qitem.find(r'/') != -1:                          # any left-hand query items containing "/" are treated as - valid or invalid - JSON pointers
                        if DEBUG:
                            print "Now calling jsonpointer_to_orms"
                        ormlist = jsonpointer_to_orms(qitem, view, view.model, qvaluelist[0])
                    else:                                                     # easiest case: qitem is not a pointer, just an immediate model attribute
                        ormlist.append(qitem)
                    if ormlist is not None and len(ormlist) != 0:
                        myQ = Q()                                         # Q is a query object for complex queries, see below
                        for ormstring in ormlist:
                            m = {ormstring : qvaluelist[0]}          # Python magic for type conversion
                            myQ= myQ | Q(**m)                       # to get multiple queries ORed together, Q objects must be used
                        try:
                            queryset = queryset.filter(myQ)
                        except FieldError:
                            raise JSONPointerException("The user entered an invalid pointer.")
                    else:                                                     # No matching path could be found
                        raise JSONPointerException("No matching model path found. The user entered an invalid pointer.")
        return queryset

# For Wildcard handling
# Takes:
# @pointer: a JSON pointer which may contain one or more wildcards (_) representing an object (not part of an object's name!)
# @model_instance: the object currently under consideration; i.e. the starting point for following the JSON pointer
# @model: model_instance's model
# @qvalue: the value the pointer is to be compared to (needed for type validation puposes)
# Returns a list of ORM paths matching the JSON pointer
# Throws JSONPointerException if pointer contains a syntax error, specifically if the leading / is missing
def jsonpointer_to_orms(pointer, model_instance, model, qvalue):
    """
    For Wildcard handling
    Takes:
    @pointer: a JSON pointer which may contain one or more wildcards (_) representing an object (not part of an object's name!)
    @model_instance: the object currently under consideration; i.e. the starting point for following the JSON pointer
    @model: model_instance's model
    @qvalue: the value the pointer is to be compared to (needed for type validation puposes)
    Returns a list of ORM paths matching the JSON pointer
    Throws JSONPointerException if pointer contains a syntax error, specifically if the leading / is missing
    """
    if DEBUG:
        print "In jsonpointer_to_orms"
    if not pointer.startswith(r'/'):                       # JSON pointers always start with /
        raise JSONPointerException("Invalid syntax: JSON pointers always start with /")
    if not pointer.startswith(r'/_/'):                # but the ORM lookup doesn't, so we need to cut it off - unless the wildcard is the first element
        if DEBUG:
            print "Cutting first /"
        pointer = pointer[1:]
    ormlist = []                                                  # ormlist will contain all wildcard- (and qvalue-) matching paths converted to ORM lookup syntax
    if pointer[-2:] == r'/_':                               # an ending wildcard needs to be amended so it will be included in the split below
        pointer = pointer + r'/'
    if pointer.find(r'/_/') != -1:                          # if there is a wildcard
        qparts = pointer.split(r'/_/')                     # split the pointer along the wildcards
        i = 0
        for qpart in qparts:
            if DEBUG:
                print "qpart[" + str(i) + "] = " + qpart
            '''if len(qpart) >= 2:                                # TODO: catch circles
                if qpart[:2] == r'_/':
                    qpart = qpart[2:]
                    qparts.insert(i, "")'''
            i+=1
        ormlist = splitlist_to_orms(qparts, ormlist, '', model_instance, model, qvalue)         # delegate the actual work; we'll receive back our list of wildcard-matching ORM paths
    else:                                                           # no wildcard, so we just need to replace the pointer markup (/) with the ORM markup (__)
        ormlist.append(pointer.replace(r'/', r'__'))
    return ormlist


def splitlist_to_orms(qparts, ormlist, path, model_instance, model, qvalue):
    """
    Does the actual work for jsonpointer_to_orms, recursively
    @qparts: the JSON pointer split along the wildcards; list will be processed first to last element
    @ormlist: will be filled through recursive calls with all wildcard- (and qvalue-) matching paths converted to ORM lookup syntax
    @model_instance: the object currently under consideration, walking along the JSON pointer/qparts
    @model: model_instance's model
    @qvalue: the value the pointer is to be compared to (needed for type validation puposes)
    Returns a list of matches
    Thows ValidationError exception if qvalue does not match the fieldtype the path ends in (to be tested)
    """
    if DEBUG:
        print "splitlist_to_orms(qparts, ormlist, " + path + ", " + model.__name__ + ", " + qvalue + ")"
        i = 0
        for qpart in qparts:
            print "qpart[" + str(i) + "] = " + qpart
            i+=1
    member = model_instance
    if qparts[0] == r'_/':                                            # if two wildcards followed each other either of this may be left over; we can treat them both as one
        qparts[0] = '_'
    if qparts[0] != '' and qparts[0] != '_':                    # if wildcard was first element or followed another wildcard the split yields '' (empty string) as first element
        cmembers = qparts[0].split(r'/')                         # considering the partial path between wildcards, split along /
        cmlen = len(cmembers)                                       # we need to keep track of how far along that partial path we are
        if DEBUG:
            print "cmlen = " + str(cmlen)
        for cmember in cmembers:				       # while we check if this explicit path up to the next wildcard is valid
            found = False
            if DEBUG:
                print "cmember = " + cmember
            cmlen-=1
            if DEBUG:
                print "cmlen = " + str(cmlen)
            try:                                                                # see if cmember (=element on explicit path) exists in current model
                #member = field instance (RelatedObject if not direct), mmodel = model (None if a local field), direct = true if field exists on model (= has instance associated), m2m = true if many-to-many relation
                member, mmodel, direct, m2m = get_model_field_by_name(model, cmember)
            except FieldDoesNotExist, exceptions.ObjectDoesNotExist:
                if DEBUG:
                    print "Could not find member " + cmember + " in model " + model.__name__
                break                                                        # if it doesn't, the path doesn't exist; DON'T try to see if anything matches later on
            if DEBUG:
                print "member = " + member.name + ", mmodel = " + (mmodel.__name__ if mmodel else "None") + ", direct = " + ("true" if direct else "false") + ", m2m = "  + ("true" if m2m else "false")
                if not direct:
                    print member. __repr__() + " can be accessed with the name " + member.get_accessor_name()
            if mmodel == None:
                try:
                    if not direct:                                            # If the m2m relationship was defined on the related element
                        mmodel = member.model                        # member is a RelatedObject and we can access its model thusly
                    else:                                                      # if it was defined on this element
                        mmodel = member.rel.to                         # this should get the model
                except AttributeError:
                    pass
            if mmodel == None:
                if len(qparts) == 1 and cmlen == 0:               # if cmember is a local field and this is the last pointer element, we have a complete and valid path
                    ormlist = add_path(ormlist, ((path + r'__') if  (path != '') else path) + member.name, member, model_instance, qvalue, False)  # which we can add to the result list
                    return ormlist
                else:
                    if DEBUG:
                        print "Breaking recursion: cmember "+ cmember + " is a local field, but pointer is not yet finished"
                    break
            else:
                if len(qparts) == 1 and cmlen == 0:               # if we've got a foreign key but the path's already finished, the path doesn't match the pointer
                    if DEBUG:
                        print "Breaking recursion: cmember "+ cmember + " is not a local field, yet the pointer is already finished"
                    break
                else:
                    found = True
            if found:                                                         # Now we should have everything and can proceed to follow our pointer
                model = mmodel			                                # ?TODO: check for circles? Probably not necessary; bounded by call
                model_instance = member
                if DEBUG:
                    print "Following member " + member.name + " of model " + model.__name__
                path = ((path + r'__') if  (path != '') else path) + (member.name if direct else member.get_accessor_name())	# and build the path we've followed in ORM syntax
            if DEBUG:
                print "path = " + path          
        if not found:                                                       # found will be false if we've broken out of the loop at any point, which means the pointer is invalid
            return ormlist                                                 # and we back up the recursion tree to try another path
        # end check: path up to wildcard is valid
    if DEBUG:
        print "end check: path up to wildcard is valid"
    if len(qparts) == 1 and qparts[0] != '_':                   # if the pointer is finished and there is no other wildcard
        if qparts[0] == '':                                              # if last element was a wildcard, add_path needs to know to intercept a ValidationError (cmp. below)
            ormlist = add_path(ormlist, path, member, model_instance, qvalue, True)   # the path is complete and valid: add to result list
        else:
            ormlist = add_path(ormlist, path, member, model_instance, qvalue, False)   # the path is complete and valid: add to result list
    else:                                                                     # if the path isn't finished and there is another wildcard
        # handle wildcard
        if DEBUG:
            print "Handle wildcard in model " + model.__name__
        # If the wildcard was the last element on the path (meaning qparts contains just one more element, an empty string '', or we had a double wildcard in which case qparts contains only the element '_')
        if (len(qparts) == 2 and qparts[1] == '') or (len(qparts) == 1 and qparts[0] == '_'):  
            members = get_local_fields(model)              	# we need to look at the local fields, not related models: all local fields end the path which can be added to ormlist if they match the type of qvalue
            for member in members:                                	# this validity check is done by add_path, in one of the two instances...
                if DEBUG:
                    print "Calling add_path with member " + member.name + " and model_instance " + model_instance.name
                ormlist = add_path(ormlist, path + r'__' + member.name, member, model_instance, qvalue, True) # ...where it is performed on the path and not the value
        else:                                                                  # if the pointer is not yet finished
            rel_objs = get_members_with_model(model)          # get all possible foreign key candidates
            if rel_objs == []:                                              # if there are no more candidates
                if DEBUG:
                    print "rel_objs is empty"
                    print "Invalid path: " + model.__name__ + " is a field"
            for obj, obj_model in rel_objs:                             # run through them all as possible matches for the wildcard
                if DEBUG:
                    print "obj = " + obj.name          
                mpath = ((path + r'__') if  (path != '') else path) + (obj.get_accessor_name() if isinstance(obj, RelatedObject) else obj.name)
                if DEBUG:
                    print "mpath = " + mpath
                if obj_model is None:                                    # Merely a precaution; this should already be sorted out by get_members_with_model
                    if DEBUG:
                        print "rel_objs is None"
                else:
                    ormlist = splitlist_to_orms(qparts[1:], ormlist, mpath, obj, obj_model, qvalue)	# descend the member tree to test if wildcard candidate is viable
    return ormlist

def add_path(ormlist, path, member, model_instance, qvalue, wildcard = False):
    """
    Validates path candidate against qvalue and, if applicable, adds it to the list of wildcard-matching paths
    @ormlist: list of all wildcard- and qvalue- matching paths converted to ORM lookup syntax
    @path: the path candidate
    @member: the field the path arrives at
    @model_instance: the object currently under consideration, which the JSON pointer ends in
    @qvalue: the value the pointer is to be compared to
    @wildcard: true if the JSON pointer ended in a wildcard; defaults to false
    Returns ormlist
    Thows ValidationError exception if qvalue does not match the fieldtype the path ends in, 
    unless wildcard is true in which case such an exception is intercepted because we're testing if the path matches the specifications;
    in all other cases the user entered an invalid query value und should be informed
    """
    if DEBUG:
        print "Add path"
        print "Member " + member.name + " of type " + type(member).__name__
        print "model_instance " + model_instance.name + " of type " + type(model_instance).__name__
        #print "Parent model: " + member.parent_model.__name__
    try:                                                                       # ensure qvalue can be converted to member field type
        member.clean(qvalue,  model_instance)
    except exceptions.ValidationError:
        print "ValidationError occurred"
        if wildcard:                                                          # the member we're trying for the wildcard doesn't fit the qvalue type; that's fine, we just disregard this path
            if DEBUG:
                print "Disregarding ValidationError because of wildcard"
        else:                                                                 # but if it wasn't a wildcard, then the user entered an invalid query value und should be informed
            raise
    else:                                                                     # path passed validation
        if DEBUG:
            print "Adding path " + path + " to list of valid paths"
        ormlist.append(path)                                            # which we can add to the result list
    return ormlist

def get_local_fields(model):
    """
    Gets all local fields of a model which aren't foreign keys
    Not identical with internal Django function of same name
    """
    myfields = []
    fields = model._meta.local_fields
    for field in fields:
        try:                                                                    # sort out all foreign keys
            model = field.rel.to
        except AttributeError:
            myfields.append(field)
    return myfields

def get_model_field_by_name(model, name):
    """
    Returns the tuple (field_object, model, direct, m2m), where field_object is the Field instance for the given name, model is the model containing this field (None for local fields), direct is True if the field exists on this model, and m2m is True for many-to-many relations. When 'direct' is False, 'field_object' is the corresponding RelatedObject for this field (since the field doesn't have an instance associated with it).
    Wrapper for internal function
    """
    return model._meta.get_field_by_name(name)

def get_members_with_model(model):
    """
    Get all foreign key members of a Django model with their related models
    Returns list of (member, model) tuples (the list may be empty, but the function won't return None)
    """
    if DEBUG:
        print "In get_members_with_model called with model " + model.__name__
    rel_objs = []
    try: 
        opts = model._meta
    except AttributeError:
        pass
    except:
        raise
    else:
        for obj in opts.fields + opts.many_to_many + opts.get_all_related_objects() + opts.get_all_related_many_to_many_objects():
            if DEBUG:
                print "obj " + obj.name + " of type " + type(obj).__name__
            try:
                model = obj.rel.to                           # will work if there's a foreign key
            except AttributeError:
                if isinstance(obj, RelatedObject):      # not quite pythonic, but obj.model will also work if obj isn't a foreign key - it will just give back the model containing the field
                    model = obj.model                      # this gets the model if there's a backward m2m relationship
                    rel_objs.append((obj, model))
                    if DEBUG:
                        print "Added tuple (" + obj.name + ", " + model.__name__ + ") to list"
            else:
                rel_objs.append((obj, model))
                if DEBUG:
                    print "Added tuple (" + obj.name + ", " + model.__name__ + ") to list"
    return rel_objs

class JSONPointerException(Exception):
    """
    Class for JSON pointer exceptions
    Raised when there is a problem with a JSON pointer
    """
    pass
