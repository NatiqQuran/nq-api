
export type RecitationsListResponseData = RecitationList[];
export interface RecitationsListRequestParams {
    limit?: number;
    mushaf: string;
    offset?: number;
    ordering?: string;
    reciter_uuid?: string;
    search?: string;
}
export interface RecitationsCreateRequestData {
    ayahs_timestamps: string;
    created_at: string;
    duration: string;
    get_mushaf_uuid: string;
    mushaf_uuid: string;
    recitation_date: string;
    recitation_location: string;
    recitation_type: string;
    reciter_account_uuid: string;
    status?: 'draft' | 'pending_review' | 'published';
    updated_at: string;
    uuid: string;
    words_timestamps: string;
}
export interface RecitationsCreateResponseData {
    ayahs_timestamps: string;
    created_at: string;
    duration: string;
    get_mushaf_uuid: string;
    mushaf_uuid: string;
    recitation_date: string;
    recitation_location: string;
    recitation_type: string;
    reciter_account_uuid: string;
    status?: 'draft' | 'pending_review' | 'published';
    updated_at: string;
    uuid: string;
    words_timestamps: string;
}
export interface RecitationsRetrieveResponseData {
    ayahs_timestamps: string;
    created_at: string;
    duration: string;
    get_mushaf_uuid: string;
    mushaf_uuid: string;
    recitation_date: string;
    recitation_location: string;
    recitation_type: string;
    reciter_account_uuid: string;
    status?: 'draft' | 'pending_review' | 'published';
    updated_at: string;
    uuid: string;
    words_timestamps: string;
}
export interface RecitationsUpdateRequestData {
    ayahs_timestamps: string;
    created_at: string;
    duration: string;
    get_mushaf_uuid: string;
    mushaf_uuid: string;
    recitation_date: string;
    recitation_location: string;
    recitation_type: string;
    reciter_account_uuid: string;
    status?: 'draft' | 'pending_review' | 'published';
    updated_at: string;
    uuid: string;
    words_timestamps: string;
}
export interface RecitationsUpdateResponseData {
    ayahs_timestamps: string;
    created_at: string;
    duration: string;
    get_mushaf_uuid: string;
    mushaf_uuid: string;
    recitation_date: string;
    recitation_location: string;
    recitation_type: string;
    reciter_account_uuid: string;
    status?: 'draft' | 'pending_review' | 'published';
    updated_at: string;
    uuid: string;
    words_timestamps: string;
}
export interface RecitationsPartialupdateRequestData {
    ayahs_timestamps?: string;
    created_at?: string;
    duration?: string;
    get_mushaf_uuid?: string;
    mushaf_uuid?: string;
    recitation_date?: string;
    recitation_location?: string;
    recitation_type?: string;
    reciter_account_uuid?: string;
    status?: 'draft' | 'pending_review' | 'published';
    updated_at?: string;
    uuid?: string;
    words_timestamps?: string;
}
export interface RecitationsPartialupdateResponseData {
    ayahs_timestamps: string;
    created_at: string;
    duration: string;
    get_mushaf_uuid: string;
    mushaf_uuid: string;
    recitation_date: string;
    recitation_location: string;
    recitation_type: string;
    reciter_account_uuid: string;
    status?: 'draft' | 'pending_review' | 'published';
    updated_at: string;
    uuid: string;
    words_timestamps: string;
}
export interface RecitationsRecitations_upload_createResponseData {
}


export interface RecitationList {
    uuid: string;
    recitation_date: string;
    recitation_location: string;
    recitation_type: string;
    duration: string;
    status?: 'draft' | 'pending_review' | 'published';
    reciter_account_uuid: string;
    mushaf_uuid: string;
    created_at: string;
    updated_at: string;
}