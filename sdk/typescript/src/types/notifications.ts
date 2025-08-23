
export type NotificationsMeGetResponseData = Notification[];
export interface NotificationsMeRequestParams {
    limit?: number;
    offset?: number;
}
export interface NotificationsOpenedGetResponseData {
}
export interface NotificationsOpenedRequestParams {
    uuid: string;
}
export interface NotificationsViewedGetResponseData {
}
export type NotificationsListResponseData = Notification[];
export interface NotificationsListRequestParams {
    limit?: number;
    offset?: number;
}
export interface NotificationsCreateRequestData {
    created_at: string;
    description?: string;
    message?: string;
    message_type?: 'success' | 'failed' | 'warning' | 'pending';
    resource_action: string;
    resource_controller: string;
    resource_uuid?: string;
    status?: 'nothing_happened' | 'got_notification' | 'viewed_notification' | 'opened_notification';
    uuid: string;
}
export interface NotificationsCreateResponseData {
    created_at: string;
    description?: string;
    message?: string;
    message_type?: 'success' | 'failed' | 'warning' | 'pending';
    resource_action: string;
    resource_controller: string;
    resource_uuid?: string;
    status?: 'nothing_happened' | 'got_notification' | 'viewed_notification' | 'opened_notification';
    uuid: string;
}
export interface NotificationsRetrieveResponseData {
    created_at: string;
    description?: string;
    message?: string;
    message_type?: 'success' | 'failed' | 'warning' | 'pending';
    resource_action: string;
    resource_controller: string;
    resource_uuid?: string;
    status?: 'nothing_happened' | 'got_notification' | 'viewed_notification' | 'opened_notification';
    uuid: string;
}
export interface NotificationsUpdateRequestData {
    created_at: string;
    description?: string;
    message?: string;
    message_type?: 'success' | 'failed' | 'warning' | 'pending';
    resource_action: string;
    resource_controller: string;
    resource_uuid?: string;
    status?: 'nothing_happened' | 'got_notification' | 'viewed_notification' | 'opened_notification';
    uuid: string;
}
export interface NotificationsUpdateResponseData {
    created_at: string;
    description?: string;
    message?: string;
    message_type?: 'success' | 'failed' | 'warning' | 'pending';
    resource_action: string;
    resource_controller: string;
    resource_uuid?: string;
    status?: 'nothing_happened' | 'got_notification' | 'viewed_notification' | 'opened_notification';
    uuid: string;
}
export interface NotificationsPartialupdateRequestData {
    created_at?: string;
    description?: string;
    message?: string;
    message_type?: 'success' | 'failed' | 'warning' | 'pending';
    resource_action?: string;
    resource_controller?: string;
    resource_uuid?: string;
    status?: 'nothing_happened' | 'got_notification' | 'viewed_notification' | 'opened_notification';
    uuid?: string;
}
export interface NotificationsPartialupdateResponseData {
    created_at: string;
    description?: string;
    message?: string;
    message_type?: 'success' | 'failed' | 'warning' | 'pending';
    resource_action: string;
    resource_controller: string;
    resource_uuid?: string;
    status?: 'nothing_happened' | 'got_notification' | 'viewed_notification' | 'opened_notification';
    uuid: string;
}


export interface Notification {
    uuid: string;
    message?: string;
    message_type?: 'success' | 'failed' | 'warning' | 'pending';
    description?: string;
    resource_controller: string;
    resource_action: string;
    resource_uuid?: string;
    status?: 'nothing_happened' | 'got_notification' | 'viewed_notification' | 'opened_notification';
    created_at: string;
}